#!/usr/bin/env python3
"""06_repair_inputs.py — pre-analysis repair: taxonomy, crosswalks, footprints.

Outputs (all under CROP_RIGIDITY_PREANALYSIS_REPAIR/ unless noted):
  FAOSTAT_CROP_ITEM_AUDIT.csv     explicit include/exclude per item_code
  SPAM_FAOSTAT_CROSSWALK.csv      FAOSTAT item -> SPAM2000 crop class
  COUNTRY_REGION_CROSSWALK.csv    FAOSTAT country -> ISO3, UN M49 (via country_converter)
  analysis/corrected_cropmix_diagnostics.csv  HHI/JSD recomputed post-audit
  analysis/footprint_cells.csv    occupied POWER-grid cells per country x SPAM crop
"""
import json
import zipfile
from pathlib import Path

import country_converter as coco
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUTDIR = ROOT / "CROP_RIGIDITY_PREANALYSIS_REPAIR"
AN = OUTDIR / "analysis"
AN.mkdir(parents=True, exist_ok=True)
LEGACY = (1981, 2000)
OUTCOME = (2001, 2020)

# ---------------------------------------------------------------- taxonomy
AGGREGATE_NAMES = {
    "Cereals", "Cereals n.e.c.", "Citrus Fruit", "Fibre Crops, Fibre Equivalent",
    "Fibre crops", "Fruit", "Oilcrops, Cake Equivalent", "Oilcrops, Oil Equivalent",
    "Pulses", "Roots and tubers", "Sugar crops", "Treenuts", "Vegetables",
    "Mixed grains",
}
NEC_PREFIXES = ("Other ", "Edible roots and tubers")

df = pd.read_feather(RAW / "faostat_qcl_2026-02-25.feather")
ha = df[(df["element"] == "Area harvested") & (df["value"] > 0)]
ha = ha[["country", "year", "item_code", "item", "value"]].copy()

items = (ha.groupby(["item_code", "item"], observed=True)["value"]
           .agg(["count", "sum"]).reset_index())
rows = []
for _, r in items.iterrows():
    name = str(r["item"])
    is_agg = name in AGGREGATE_NAMES
    is_nec = name.startswith(NEC_PREFIXES) or " n.e.c." in name
    overlap = ""
    if is_agg:
        overlap = "parent aggregate of member items"
    elif is_nec:
        overlap = "residual class - exclusive by FAOSTAT definition"
    elif name in {"Broad beans", "Broad beans and horse beans, green",
                  "Beans, dry", "Beans, green", "Peas, dry", "Peas, green",
                  "Chillies and peppers", "Chillies and peppers, green (Capsicum spp. and Pimenta spp.)",
                  "Onions", "Onions and shallots, green",
                  "Maize", "Green maize", "Melon", "Watermelons"}:
        overlap = "green/dry sibling item pair - kept, flagged"
    include = not is_agg
    rows.append(dict(
        item_code=str(r["item_code"]).lstrip("0") or "0",
        item_name=name,
        include_primary=int(include),
        reason=("excluded: cross-crop aggregate" if is_agg else
                ("kept: exclusive residual (n.e.c.) class" if is_nec else "kept: single crop")),
        aggregate_group=("aggregate" if is_agg else ("nec-residual" if is_nec else "single")),
        possible_overlap=overlap or "none",
    ))
audit = pd.DataFrame(rows)
audit.to_csv(OUTDIR / "FAOSTAT_CROP_ITEM_AUDIT.csv", index=False)

keep_items = set(audit.loc[audit.include_primary == 1, "item_name"])
ha2 = ha[ha["item"].isin(keep_items)]

# ------------------------------------------------- corrected mix diagnostics
def shares(d):
    s = d.groupby(["country", "item"], observed=True)["value"].mean().reset_index()
    s["share"] = s["value"] / s.groupby("country", observed=True)["value"].transform("sum")
    return s

def js_distance(p, q):
    m = 0.5 * (p + q)
    klp = np.where(p > 0, p * np.log(p / m), 0).sum()
    klq = np.where(q > 0, q * np.log(q / m), 0).sum()
    return float(np.sqrt(0.5 * klp + 0.5 * klq))

recs = []
for c, g in ha2.groupby("country", observed=True):
    gl = g[(g.year >= LEGACY[0]) & (g.year <= LEGACY[1])]
    go = g[(g.year >= OUTCOME[0]) & (g.year <= OUTCOME[1])]
    if gl.year.nunique() < 10 or go.year.nunique() < 10:
        continue
    sl, so = shares(gl), shares(go)
    if sl.item.nunique() < 4 or so.item.nunique() < 4:
        continue
    p = sl.set_index("item")["share"]
    q = so.set_index("item")["share"]
    idx = sorted(set(p.index) | set(q.index))
    p, q = p.reindex(idx, fill_value=0.0), q.reindex(idx, fill_value=0.0)
    recs.append(dict(
        country=c, n_crops=sl.item.nunique(),
        hhi=(p ** 2).sum(), entropy=-(p[p > 0] * np.log(p[p > 0])).sum(),
        top1=p.max(), top3=p.sort_values(ascending=False).head(3).sum(),
        dominant_crop=p.idxmax(), jsd=js_distance(p.values, q.values),
        replaced=int(p.idxmax() != q.idxmax()),
        delta_hhi=(q ** 2).sum() - (p ** 2).sum(),
    ))
corr = pd.DataFrame(recs)
old = pd.read_csv(ROOT / "analysis" / "design_diagnostics_summary.csv")
cmp_ = corr.merge(old, on="country", suffixes=("_new", "_old"))
for col in ("hhi", "jsd"):
    corr[f"{col}_delta_vs_old"] = corr[col] - cmp_.set_index("country")[f"{col}_old"].reindex(corr.country).values
corr.to_csv(AN / "corrected_cropmix_diagnostics.csv", index=False)
print("corrected diagnostics:", len(corr), "countries; median dHHI",
      corr.hhi_delta_vs_old.median(), "dJSD", corr.jsd_delta_vs_old.median())

# ---------------------------------------------------------------- crosswalk
SPAM = {
    "WHEA": ["Wheat"],
    "RICE": ["Rice"],
    "MAIZ": ["Maize", "Green maize"],
    "BARL": ["Barley"],
    "MILL": ["Millet"],
    "SORG": ["Sorghum"],
    "POTA": ["Potatoes"],
    "SWPY": ["Sweet potatoes", "Yams", "Yautia", "Taro",
             "Edible roots and tubers with high starch or inulin content, n.e.c., fresh"],
    "CASS": ["Cassava", "Cassava leaves"],
    "BANP": ["Bananas", "Plantains"],
    "SOYB": ["Soybeans"],
    "BEAN": ["Beans, dry", "Beans, green", "Broad beans",
             "Broad beans and horse beans, green", "String beans"],
    "OPUL": ["Peas, dry", "Peas, green", "Chickpeas", "Cow peas", "Pigeon peas",
             "Lentils", "Bambara beans, dry", "Lupins", "Vetches", "Other pulses n.e.c."],
    "GROU": ["Groundnuts"],
    "COTT": ["Seed cotton"],
    "COFF": ["Coffee, green"],
    "SUGC": ["Sugar cane"],
    "SUGB": ["Sugar beet"],
    "OFIB": ["Jute", "Abaca, manila hemp, raw", "Sisal, raw", "Ramie, raw or retted",
             "Flax, raw or retted", "True hemp, raw or retted",
             "Kenaf, and other textile bast fibres, raw or retted",
             "Agave fibres, raw, n.e.c.", "Kapok fibre, raw"],
    "OOIL": ["Rapeseed", "Sunflower seed", "Sesame seed", "Safflower seed",
             "Mustard seed", "Linseed", "Hempseed", "Poppy seeds",
             "Olives", "Coconuts", "Palm fruit oil", "Castor oil seed",
             "Jojoba seeds", "Tung nuts", "Karite nuts", "Kapok fruit",
             "Tallowtree seeds", "Melonseed", "Other oil seeds, n.e.c.",
             "Oilcrops, Oil Equivalent"],
    "OTHE": ["Oats", "Rye", "Buckwheat", "Triticale", "Canary seed", "Quinoa",
             "Fonio", "Mixed grains", "Cereals n.e.c.",
             "Cocoa beans", "Tea", "Tobacco", "Natural rubber in primary forms",
             "Hop cones", "Maté leaves", "Pyrethrum, dried flowers",
             "Vanilla, raw", "Cloves (whole stems), raw",
             "Cinnamon and cinnamon-tree flowers, raw",
             "Nutmeg, mace, cardamoms, raw", "Pepper", "Ginger, raw",
             "Kola nuts", "Locust beans (carobs)", "Peppermint, spearmint",
             "Other stimulant, spice and aromatic crops, n.e.c.",
             "Other sugar crops n.e.c.",
             "Apples", "Pears", "Peaches and nectarines", "Plums", "Apricots",
             "Cherries", "Sour cherries", "Quinces", "Other pome fruits",
             "Other stone fruits", "Grapes", "Figs", "Dates",
             "Oranges", "Lemons and limes", "Grapefruit",
             "Tangerines", "Other citrus fruit, n.e.c.",
             "Mangoes", "Pineapples", "Papayas", "Avocados", "Persimmons",
             "Other tropical fruits, n.e.c.", "Other fruits, n.e.c.",
             "Bananas n.e.c.",
             "Strawberries", "Raspberries", "Blueberries", "Cranberries",
             "Gooseberries", "Currants", "Kiwi",
             "Other berries and fruits of the genus vaccinium n.e.c.",
             "Almonds", "Walnuts", "Hazelnuts", "Chestnut", "Pistachios",
             "Cashew nuts", "Cashewapple", "Brazil nuts, with shell",
             "Areca nuts", "Other nuts (excluding wild edible nuts and groundnuts), in shell, n.e.c.",
             "Tomatoes", "Onions", "Onions and shallots, green", "Garlic",
             "Cabbages", "Cauliflowers and broccoli", "Lettuce", "Spinach",
             "Carrots and turnips", "Cucumbers and gherkins",
             "Pumpkins, squash and gourds", "Eggplants", "Okra", "Artichokes",
             "Asparagus", "Leeks", "Melon", "Watermelons",
             "Chillies and peppers", "Chillies and peppers, green (Capsicum spp. and Pimenta spp.)",
             "Other vegetables, fresh n.e.c.", "Herbs", "Mushrooms n.e.c.",
             "Chicory roots"],
}
inv = {n.strip(): c for c, names in SPAM.items() for n in names}
xw = []
for _, r in audit.iterrows():
    xw.append(dict(item_code=r.item_code, item_name=r.item_name,
                   spam_crop=inv.get(str(r.item_name).strip(), "none"),
                   crosswalk_status=("mapped" if str(r.item_name).strip() in inv
                                     else "no SPAM class")))
xwd = pd.DataFrame(xw)
xwd.to_csv(OUTDIR / "SPAM_FAOSTAT_CROSSWALK.csv", index=False)
print("crosswalk unmatched:", xwd.loc[xwd.spam_crop == 'none', 'item_name'].tolist())

# --------------------------------------------------------------- countries
cc = coco.CountryConverter()
countries = sorted(ha2["country"].unique())
HISTORICAL = {"USSR", "Yugoslavia", "Czechoslovakia", "Ethiopia (former)",
              "Sudan (former)", "Belgium-Luxembourg (FAO)", "Serbia and Montenegro",
              "China (FAO)"}
AGGREGATE_PATTERNS = ("(FAO)", "countries", "Countries", "Union", "World",
                      "Developing States")
AGGREGATE_EXACT = {"Africa", "Asia", "Europe", "Oceania", "South America",
                   "Net Food Importing Developing Countries (FAO)",
                   "World", "European Union (27)"}

def _conv(name, to):
    r = np.atleast_1d(cc.convert(names=[name], to=to))
    return str(r[0])

crows = []
for cname in countries:
    iso3 = "none"; region = "none"; sub = "none"; status = "mapped"
    if (cname in HISTORICAL or cname in AGGREGATE_EXACT
            or any(p in cname for p in AGGREGATE_PATTERNS)):
        status = "historical/aggregate entity - excluded from estimation set, not silently reassigned"
    else:
        iso3 = _conv(cname, "ISO3")
        sub = _conv(cname, "UNregion")
        region = _conv(cname, "continent")
        if iso3 in {"not found", "nan"} or len(iso3) != 3:
            status = "unresolved"; iso3 = "none"; sub = "none"; region = "none"
    crows.append(dict(faostat_country=cname, iso3=iso3, region=region,
                      subregion=sub, mapping_source="country_converter UN/ISO (UN M49-aligned)",
                      status=status))
cwd = pd.DataFrame(crows)
cwd.to_csv(OUTDIR / "COUNTRY_REGION_CROSSWALK.csv", index=False)
print("unresolved:", cwd[cwd.status != "mapped"].faostat_country.tolist())

# --------------------------------------------------------------- footprints
import gc
del df, ha, ha2
gc.collect()

zpath = RAW / "mapspam" / "spam2000v3.0.7_global_harvested-area.dbf-csv.zip"
spam_cols = ["whea", "rice", "maiz", "barl", "mill", "sorg", "pota", "swpy",
             "cass", "banp", "soyb", "bean", "opul", "sugc", "sugb", "coff",
             "cott", "ofib", "grou", "ooil", "othe"]
rec = []
with zipfile.ZipFile(zpath) as zf:
    with zf.open("spam_h.csv") as fh:
        sp = pd.read_csv(fh, usecols=["stat_code", "x", "y"] + spam_cols)
# SPAM2000 stat_code uses FIPS province codes for some countries; map the
# 2-letter prefix to ISO3 (verified against pixel centroid geography).
PREFIX = {"BY": "BDI", "CG": "COD", "CT": "CAF", "GB": "GAB", "KE": "KEN",
          "LI": "LBR", "MR": "MRT", "NI": "NGA", "RW": "RWA", "SF": "ZAF",
          "TO": "TGO", "TZ": "TZA", "UG": "UGA", "ZI": "ZWE"}
sp["iso3"] = sp.stat_code.where(sp.stat_code.str.len() == 3,
                              sp.stat_code.str[:2].map(PREFIX))
est = set(cwd.loc[cwd.status == "mapped", "iso3"])
sp = sp[sp.iso3.isin(est)]
for iso, g in sp.groupby("iso3"):
    for col in spam_cols:
        sub = g[g[col] > 0]
        if len(sub) == 0:
            continue
        blat = np.round(sub.y.values / 0.5) * 0.5
        blon = np.round(sub.x.values / 0.625) * 0.625
        cells = sorted(set(zip(np.round(blon, 3), np.round(blat, 3))))
        rec.append(dict(iso3=iso.upper(), spam_crop=col.upper(), n_spam_cells=len(sub),
                        n_power_cells=len(cells),
                        lon_min=min(blon), lon_max=max(blon),
                        lat_min=min(blat), lat_max=max(blat),
                        cells_json=json.dumps(cells)))
fcells = pd.DataFrame(rec)
fcells.to_csv(AN / "footprint_cells.csv", index=False)
print("footprint rows:", len(fcells))
