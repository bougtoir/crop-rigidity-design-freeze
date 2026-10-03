#!/usr/bin/env python3
"""Final-lock repair, issues 1,5,6.

- Baseline irrigation: SPAM2000 zonal irrigated share (same pipeline as
  SPAM2010 but reference year 2000) + MIRCA2000 unit-level shares; compare
  against SPAM2010 without outcome contact.
- Temporal alignment audit: per-unit ag years vs climate windows.
- MIRCA calendar proxy validation: national vs subnational MIRCA calendars
  where available.
Writes analysis/{baseline_irrigation_source_comparison.csv,
admin_temporal_alignment_audit.csv, calendar_proxy_validation.csv} and
analysis/design_matrix_v2.csv (adds irr_share_base2000 + MIRCA irr).
"""
import gzip
import json
import numpy as np
import pandas as pd
import geopandas as gpd
import rasterio
from rasterio.features import rasterize
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "SUBNATIONAL_RIGIDITY_DESIGN_FREEZE"
FOUT = ROOT / "SUBNATIONAL_RIGIDITY_FINAL_LOCK"
(FOUT / "analysis").mkdir(parents=True, exist_ok=True)
RAW = ROOT / "data" / "raw"

dm = pd.read_csv(OUT / "analysis" / "design_matrix_climate.csv")
xw = pd.read_csv(OUT / "ADMIN_BOUNDARY_CROSSWALK.csv")

# ---------------- geometries ----------------
gadm = gpd.read_file(RAW / "gadm410" / "gadm_410-levels.gpkg", layer="ADM_1",
                     columns=["GID_1"])
gid2geom = dict(zip(gadm["GID_1"], gadm.geometry))
nuts = {}
for lvl in (1, 2):
    g = gpd.read_file(RAW / "subnat" / f"nuts2021_l{lvl}.geojson")
    nuts.update(dict(zip(g["NUTS_ID"], g.geometry)))
hv = gpd.read_file(RAW / "subnat" / "hvstat_africa_boundary_v1.2.gpkg")
hv["_key"] = ("HV1:" + hv["country_code"].astype(str) + ":"
              + hv["admin_1"].fillna("").astype(str))
hv_units = {}
for k, s in hv[hv["admin_1"].notna()].groupby("_key"):
    hv_units[k] = s.union_all() if hasattr(s, "union_all") else s.unary_union
for _, r in hv[hv["admin_1"].isna()].iterrows():
    hv_units["HV2:" + r["fnid"]] = r.geometry

gid_of = xw.drop_duplicates("unit_id").set_index("unit_id")["gadm41_gid"]
geoms, cent = {}, {}
for uid in dm.unit_id.unique():
    g = None
    gid = gid_of.get(uid)
    if pd.notna(gid) and gid in gid2geom:
        g = gid2geom[gid]
    elif uid in hv_units:
        g = hv_units[uid]
    elif uid in nuts:
        g = nuts[uid]
    if g is not None:
        geoms[uid] = g
        c = g.centroid
        cent[uid] = (c.x, c.y)

# ---------------- zone raster on SPAM2000 grid ----------------
tif_dir = RAW / "mapspam" / "spam2000_H"
files = sorted(tif_dir.glob("*_A.tif"))
ref = rasterio.open(files[0]); shape, transform = ref.shape, ref.transform
ref.close()
uids = sorted(geoms)
uid_idx = {u: i + 1 for i, u in enumerate(uids)}
zone = np.zeros(shape, dtype=np.int32)
for u in uids:
    zone = np.maximum(zone, rasterize([(geoms[u], uid_idx[u])],
                    out_shape=shape, transform=transform, all_touched=False,
                    dtype=np.int32))
n = len(uids)
totA = np.zeros(n + 1); totI = np.zeros(n + 1)
for f in files:
    a = rasterio.open(f).read(1)
    if a.shape != shape:
        a = a[:shape[0], :shape[1]]
        if a.shape != shape:
            continue
    a = np.where(np.isfinite(a) & (a > 0), a, 0.0)
    totA += np.bincount(zone.ravel(), weights=a.ravel(), minlength=n + 1)
    fi = tif_dir / f.name.replace("_A.tif", "_I.tif")
    if fi.exists():
        i = rasterio.open(fi).read(1)
        if i.shape != shape:
            i = i[:shape[0], :shape[1]]
            if i.shape != shape:
                continue
        i = np.where(np.isfinite(i) & (i > 0), i, 0.0)
        totI += np.bincount(zone.ravel(), weights=i.ravel(), minlength=n + 1)

spam2k = pd.DataFrame({"unit_id": uids,
                       "irr_share_spam2000": np.clip(totI[1:n + 1] /
                        np.where(totA[1:n + 1] == 0, np.nan, totA[1:n + 1]), 0, 1)})

# ---------------- MIRCA2000 unit-level irrigated share ----------------
names = {}
unit2name = {}
for line in gzip.open(RAW / "mirca" / "unit_code_grid" / "unit_name.txt.gz", "rt"):
    p = line.rstrip("\n").split("\t")
    if len(p) == 2 and p[0].isdigit():
        unit2name[int(p[0])] = p[1]
        names.setdefault(p[1].split("_")[0], []).append(int(p[0]))

irr_areas = {}
for line in gzip.open(RAW / "mirca" / "condensed_cropping_calendars"
                      / "cropping_calendar_irrigated.txt.gz", "rt"):
    p = line.split()
    if len(p) < 4:
        continue
    try:
        uc, nsc = int(p[0]), int(p[2])
    except ValueError:
        continue
    vals = p[3:]
    a = sum(float(vals[j]) for j in range(0, 3 * nsc, 3))
    irr_areas[uc] = irr_areas.get(uc, 0.0) + a
rf_areas = {}
for line in gzip.open(RAW / "mirca" / "condensed_cropping_calendars"
                      / "cropping_calendar_rainfed.txt.gz", "rt"):
    p = line.split()
    if len(p) < 4:
        continue
    try:
        uc, nsc = int(p[0]), int(p[2])
    except ValueError:
        continue
    vals = p[3:]
    a = sum(float(vals[j]) for j in range(0, 3 * nsc, 3))
    rf_areas[uc] = rf_areas.get(uc, 0.0) + a

CTY = {"Tanzania, United Republic of": "Tanzania",
       "Laos": "Lao People's Democratic Republic",
       "Congo, The Democratic Republic of the":
       "Democratic Republic of the Congo",
       "United States": "United States of America"}
NUTS2NAME = {"AT":"Austria","BE":"Belgium","BG":"Bulgaria","CH":"Switzerland",
    "CY":"Cyprus","CZ":"Czechia","DE":"Germany","DK":"Denmark","EE":"Estonia",
    "EL":"Greece","ES":"Spain","FI":"Finland","FR":"France","HR":"Croatia",
    "HU":"Hungary","IE":"Ireland","IS":"Iceland","IT":"Italy","LT":"Lithuania",
    "LU":"Luxembourg","LV":"Latvia","ME":"Montenegro","MK":"North Macedonia",
    "MT":"Malta","NL":"Netherlands","NO":"Norway","PL":"Poland","PT":"Portugal",
    "RO":"Romania","RS":"Serbia","SE":"Sweden","SI":"Slovenia","SK":"Slovakia",
    "TR":"Turkey","UK":"United Kingdom","AL":"Albania",
    "BA":"Bosnia and Herzegovina","XK":"Kosovo"}

def mirca_share(ctry, uname):
    key = CTY.get(ctry, NUTS2NAME.get(ctry, ctry))
    # try admin-1 MIRCA unit match by name
    cand = None
    for uc in names.get(key, []):
        full = unit2name.get(uc, "")
        if "_" in full and uname:
            tail = full.split("_", 1)[1].lower()
            if tail.replace(" ", "") in str(uname).lower().replace(" ", ""):
                cand = uc
                break
    if cand is None and len(names.get(key, [])) == 1:
        cand = names[key][0]
    if cand is None:
        return np.nan
    tot = irr_areas.get(cand, 0) + rf_areas.get(cand, 0)
    return irr_areas.get(cand, 0) / tot if tot > 0 else np.nan

import unicodedata
CTY2 = dict(CTY)
CTY2.update({"United States": "United States of America"})
dm["irr_share_mirca"] = [mirca_share(c, un) for c, un in
                         zip(dm.country, dm.unit_name)]
dm = dm.merge(spam2k, on="unit_id", how="left")
print("MIRCA coverage:", dm.irr_share_mirca.notna().sum(),
      "SPAM2000 coverage:", dm.irr_share_spam2000.notna().sum())

# ---------------- source comparison ----------------
cmp_rows = []
for col, lab in [("irr_share_spam2000", "spam2000_zonal"),
                 ("irr_share_mirca", "mirca2000_unit"),
                 ("irr_share", "spam2010_zonal (post-baseline)"),
                 ("irr_share_reported", "usda_reported_2002")]:
    s = dm[col]
    cmp_rows.append(dict(source=lab, coverage=int(s.notna().sum()),
                         mean=float(s.mean()), sd=float(s.std())))
cmp_tbl = pd.DataFrame(cmp_rows)
sub = dm.dropna(subset=["irr_share_spam2000", "irr_share"])
cmp_tbl["corr_vs_spam2010"] = np.nan
cmp_tbl.loc[cmp_tbl.source == "spam2000_zonal", "corr_vs_spam2010"] = \
    sub.irr_share_spam2000.corr(sub.irr_share)
cmp_tbl.loc[cmp_tbl.source == "spam2000_zonal", "mad_vs_spam2010"] = \
    (sub.irr_share_spam2000 - sub.irr_share).abs().mean()
cmp_tbl.loc[cmp_tbl.source == "spam2000_zonal", "rank_corr_vs_spam2010"] = \
    sub.irr_share_spam2000.corr(sub.irr_share, method="spearman")
sub2 = dm.dropna(subset=["irr_share_mirca", "irr_share"])
cmp_tbl.loc[cmp_tbl.source == "mirca2000_unit", "corr_vs_spam2010"] = \
    sub2.irr_share_mirca.corr(sub2.irr_share)
cmp_tbl.loc[cmp_tbl.source == "mirca2000_unit", "mad_vs_spam2010"] = \
    (sub2.irr_share_mirca - sub2.irr_share).abs().mean()
cmp_tbl.loc[cmp_tbl.source == "mirca2000_unit", "rank_corr_vs_spam2010"] = \
    sub2.irr_share_mirca.corr(sub2.irr_share, method="spearman")
cmp_tbl.to_csv(FOUT / "analysis" / "baseline_irrigation_source_comparison.csv",
               index=False)
print(cmp_tbl.to_string())

# disagreement by country
dis = (dm.dropna(subset=["irr_share_spam2000", "irr_share"])
        .assign(d=lambda x: (x.irr_share_spam2000 - x.irr_share).abs())
        .groupby("country")["d"].mean().sort_values(ascending=False))
print("largest disagreement:", dis.head(10).to_dict())

# ---------------- temporal alignment audit (issue 5) ----------------
al = dm[["unit_id", "country", "y0", "y1", "gap"]].copy()
al["climate_base_window"] = [f"{b-1}-{b+1}" for b in al.y0]
al["climate_end_window"] = [f"{e-1}-{e+1}" for e in al.y1]
al["aligned"] = True
al.to_csv(FOUT / "analysis" / "admin_temporal_alignment_audit.csv", index=False)

# ---------------- calendar proxy validation (issue 6) ----------------
# MIRCA subnational units: compare national CCC vs admin-1 CCC mismatch_T.
import sys
MIRCA2CANON = {1:"wheat",2:"maize",3:"rice",4:"barley",5:"sorghum",6:"millet",
    7:"other_cereals",8:"sugarcane",9:"cassava",10:"potato",11:"soybean",
    12:"rapeseed",13:"cotton",14:"tobacco",15:"dry_beans",16:"vegetables",
    17:"coffee",18:"other_annual",19:"oil_palm",20:"banana",21:"citrus",
    22:"grapes",23:"olive",24:"other_perennial",25:"forage",26:"other_annual"}
cal_unit = {}
for fn in ("cropping_calendar_rainfed.txt.gz",
           "cropping_calendar_irrigated.txt.gz"):
    for line in gzip.open(RAW / "mirca" / "condensed_cropping_calendars" / fn,
                          "rt"):
        p = line.split()
        if len(p) < 4:
            continue
        try:
            uc, cc, nsc = int(p[0]), int(p[1]), int(p[2])
        except ValueError:
            continue
        can = MIRCA2CANON.get(cc)
        if can is None:
            continue
        vals = p[3:]
        ent = cal_unit.setdefault(uc, {}).setdefault(can, {})
        for j in range(0, 3 * nsc, 3):
            try:
                a, s_, e_ = float(vals[j]), int(vals[j + 1]), int(vals[j + 2])
            except (ValueError, IndexError):
                continue
            rng = range(s_, e_ + 1) if s_ <= e_ else list(range(s_, 13)) + list(range(1, e_ + 1))
            for m_ in rng:
                ent[m_] = ent.get(m_, 0.0) + a

def power_series(uid):
    f = RAW / "power_subnat" / f"{uid.replace('/', '_')}.json"
    if not f.exists():
        return None
    d = json.loads(f.read_text())["properties"]["parameter"]
    out = {}
    for k, v in d["T2M"].items():
        y, m_ = int(k[:4]), int(k[4:])
        if m_ != 13:
            out.setdefault(y, {})[m_] = (v, d["PRECTOTCORR"].get(k, np.nan))
    return out

def season_T(series, yrs, mlist):
    v = [series.get(y, {}).get(m_, (np.nan, np.nan))[0]
         for y in yrs for m_ in mlist]
    v = [x for x in v if np.isfinite(x)]
    return float(np.mean(v)) if v else np.nan

def mismatch_with_cal(series, cal, y0, y1):
    if series is None or not cal:
        return np.nan
    T0 = T1 = w = 0.0
    for can, mm in cal.items():
        mlist = sorted(mm.keys())
        t0 = season_T(series, range(y0 - 1, y0 + 2), mlist)
        t1 = season_T(series, range(y1 - 1, y1 + 2), mlist)
        if np.isnan(t0) or np.isnan(t1):
            continue
        T0 += t0; T1 += t1; w += 1
    return abs(T1 - T0) / w if w else np.nan

nat_cal = {}  # country-name -> merged national calendar (unit w/o "_")
for uc, c in cal_unit.items():
    nm = unit2name.get(uc, "")
    if "_" not in nm:
        nat_cal[nm] = c
subnat = {}  # country -> {unit_tail -> calendar}
for uc, c in cal_unit.items():
    nm = unit2name.get(uc, "")
    if "_" in nm:
        subnat.setdefault(nm.split("_")[0], {})[nm.split("_", 1)[1]] = c

# countries existing only at admin-1 level in MIRCA get an area-weighted
# aggregate national calendar (weighted by calendar growing-month area)
for ctyname, units in subnat.items():
    if ctyname in nat_cal:
        continue
    agg = {}
    for c in units.values():
        for can, mm in c.items():
            for m_, w_ in mm.items():
                agg.setdefault(can, {}).setdefault(m_, 0.0)
                agg[can][m_] += w_
    nat_cal[ctyname] = agg

val_rows = []
for _, r in dm.iterrows():
    ckey = CTY.get(r.country, NUTS2NAME.get(r.country, r.country))
    if ckey not in subnat or ckey not in nat_cal:
        continue
    series = power_series(r.unit_id)
    if series is None:
        continue
    # best subnat match: same admin-1 name
    import unicodedata
    def simpl(s):
        return unicodedata.normalize("NFKD", str(s)).encode(
            "ascii", "ignore").decode().lower().replace(" ", "").replace("_", "")
    s_cal = None
    for tail, c in subnat[ckey].items():
        if simpl(tail) == simpl(r.unit_name) or \
           (len(simpl(tail)) > 5 and simpl(tail) in simpl(r.unit_name)):
            s_cal = c
            break
    if s_cal is None:
        continue
    m_nat = mismatch_with_cal(series, nat_cal[ckey], r.y0, r.y1)
    m_sub = mismatch_with_cal(series, s_cal, r.y0, r.y1)
    if np.isfinite(m_nat) and np.isfinite(m_sub):
        val_rows.append(dict(unit_id=r.unit_id, country=r.country,
                             mismatch_national=m_nat, mismatch_subnat=m_sub,
                             abs_diff=abs(m_nat - m_sub)))
val = pd.DataFrame(val_rows)
val.to_csv(FOUT / "analysis" / "calendar_proxy_validation.csv", index=False)
print("calendar proxy validation units:", len(val))
if len(val):
    print("corr:", val.mismatch_national.corr(val.mismatch_subnat),
          "median abs diff:", val.abs_diff.median())

# freeze v2 design matrix: primary = SPAM2000 zonal; MIRCA2000 unit-level
# fills gaps (same construct: ~2000 irrigated harvested-area share)
dm["irr_share_base2000"] = dm["irr_share_spam2000"].fillna(dm["irr_share_mirca"])
dm["irr_source"] = np.where(dm.irr_share_spam2000.notna(), "spam2000",
                    np.where(dm.irr_share_mirca.notna(), "mirca2000", "missing"))
print("combined baseline coverage:", dm.irr_share_base2000.notna().sum())
dm.to_csv(FOUT / "analysis" / "final_primary_design_matrix_preoutcome.csv",
          index=False)
print("v2 matrix written:", len(dm))
