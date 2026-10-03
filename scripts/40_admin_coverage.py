#!/usr/bin/env python3
"""Phase 1-2: build the unified admin-level crop observation matrix.

Reads persisted raw downloads under data/raw/subnat/ and emits:
  analysis/admin_crop_observation_matrix.parquet
  analysis/admin_unit_coverage.csv
Columns: country, iso3, unit_id, unit_name, admin_level, year, crop, area_ha, source
"""
import gzip
import zipfile
import pandas as pd
import numpy as np
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "subnat"
OUT = ROOT / "SUBNATIONAL_RIGIDITY_DESIGN_FREEZE" / "analysis"
OUT.mkdir(parents=True, exist_ok=True)
ACRE = 0.404685642

frames = []

# ---- 1. HarvestStat Africa v1.2 -------------------------------------------
d = pd.read_csv(RAW / "hvstat_africa_data_v1.2.csv", low_memory=False)
d = d[["country", "country_code", "fnid", "admin_1", "admin_2", "product",
       "planting_year", "area"]].copy()
d["year"] = pd.to_numeric(d["planting_year"], errors="coerce")
d = d.dropna(subset=["year", "area"])
d = d.assign(iso3=d["country_code"],
             unit_id="HV1:" + d["country_code"].astype(str) + ":"
                     + d["admin_1"].fillna("").astype(str),
             unit_name=d["admin_1"].fillna(d["admin_2"]),
             admin_level=1, crop=d["product"].str.lower().str.strip(),
             area_ha=d["area"], source="harveststat_africa_v1.2")
d.loc[d["admin_1"].isna(), "admin_level"] = 2
d.loc[d["admin_1"].isna(), "unit_id"] = ("HV2:" + d["fnid"].astype(str))
frames.append(d[["country", "iso3", "unit_id", "unit_name", "admin_level",
                 "year", "crop", "area_ha", "source"]])
print("harveststat", len(d))

# ---- 2. FAO sub-national agricultural statistics ---------------------------
d = pd.read_csv(RAW / "fao_subnational_stats.csv", low_memory=False)
d = d[(d["TOPOLOGICAL_LEVEL"] == 1) & (d["METRIC"] == "Harvested Area")].copy()
d["area_ha"] = pd.to_numeric(d["VALUE"], errors="coerce")
d.loc[d["UNIT"].astype(str).str.contains("1000", na=False), "area_ha"] *= 1000
d = d.dropna(subset=["area_ha"])
d = d.assign(iso3=None, unit_id="GADM:" + d["GADM_CODE"].astype(str),
             unit_name=d["REGION_NAME"], admin_level=1,
             crop=d["COMMON_PRODUCT_NAME"].str.lower().str.strip(),
             year=d["YEAR"].astype(int), source="fao_subnational_2024")
d = d.rename(columns={"COUNTRY_NAME": "country"})
frames.append(d[["country", "iso3", "unit_id", "unit_name", "admin_level",
                 "year", "crop", "area_ha", "source"]])
print("fao subnat", len(d))

# ---- 3. Eurostat apro_cpshr (NUTS2 preferred, NUTS1 kept) ------------------
rows = []
with open(RAW / "apro_cpshr.tsv") as f:
    years = f.readline().rstrip("\n").split("\t")[1:]
    years = [int(y) for y in years]
    for line in f:
        p = line.rstrip("\n").split("\t")
        dims = p[0].split(",")
        if dims[2] != "MAR_THS_HA":
            continue
        geo = dims[3]
        lev = {3: 1, 4: 2}.get(len(geo) - len("".join(ch for ch in geo if ch.isalpha())) + 2, None)
        for y, v in zip(years, p[1:]):
            v = v.strip()
            if v in (":", "", "z"):
                continue
            try:
                ha = float(v.split(" ")[0]) * 1000.0
            except ValueError:
                continue
            rows.append((geo, dims[1], y, ha))
eu = pd.DataFrame(rows, columns=["unit_id", "crop", "year", "area_ha"])
eu["admin_level"] = np.where(eu["unit_id"].str.len() == 4, 2, 1)
eu["country"] = eu["unit_id"].str[:2]
eu["unit_name"] = eu["unit_id"]
eu["iso3"] = None
eu["crop"] = eu["crop"].str.lower()
eu["source"] = "eurostat_apro_cpshr_2026"
frames.append(eu[["country", "iso3", "unit_id", "unit_name", "admin_level",
                  "year", "crop", "area_ha", "source"]])
print("eurostat", len(eu))

# ---- 4. Statistics Canada 32-10-0359 (provincial, admin-1) -----------------
d = pd.read_csv(RAW / "32100359.csv")
d = d[d["Harvest disposition"].str.contains("Harvested area", na=False) |
      d["Harvest disposition"].str.contains("Seeded area", na=False)]
pref = d["Harvest disposition"].str.contains("Harvested")
d = d[pref | ~d.duplicated(["REF_DATE", "GEO", "Type of crop"], keep=False)]
d = d[d["UOM"] == "Acres"]
d = d[~d["GEO"].isin(["Canada", "Maritime provinces", "Prairie provinces",
                      "East", "West"])].copy()
d = d.assign(iso3="CAN", unit_id="CA:" + d["GEO"], unit_name=d["GEO"],
             admin_level=1, crop=d["Type of crop"].str.lower().str.strip(),
             year=d["REF_DATE"].astype(int), area_ha=d["VALUE"] * ACRE,
             source="statcan_32100359")
d = d.rename(columns={"GEO": "country"})
d["country"] = "Canada"
frames.append(d[["country", "iso3", "unit_id", "unit_name", "admin_level",
                 "year", "crop", "area_ha", "source"]])
print("statcan", len(d))

# ---- 5. USDA Census county -> state admin-1 --------------------------------
d = pd.read_csv(RAW / "usda_census_county_area.csv")
d["area_acres"] = pd.to_numeric(d["value_acres"].astype(str).str.replace(",", ""),
                                 errors="coerce")
d = d.dropna(subset=["area_acres"])
st = {"{:02d}".format(int(f)): f for f in d["state_fips"].unique()}
d["unit_id"] = d["state_fips"].apply(lambda x: "US:" + str(int(x)).zfill(2))
d = d.groupby(["year", "unit_id", "crop"], as_index=False)["area_acres"].sum()
US_STATES = {"01":"Alabama","02":"Alaska","04":"Arizona","05":"Arkansas","06":"California","08":"Colorado","09":"Connecticut","10":"Delaware","11":"District of Columbia","12":"Florida","13":"Georgia","15":"Hawaii","16":"Idaho","17":"Illinois","18":"Indiana","19":"Iowa","20":"Kansas","21":"Kentucky","22":"Louisiana","23":"Maine","24":"Maryland","25":"Massachusetts","26":"Michigan","27":"Minnesota","28":"Mississippi","29":"Missouri","30":"Montana","31":"Nebraska","32":"Nevada","33":"New Hampshire","34":"New Jersey","35":"New Mexico","36":"New York","37":"North Carolina","38":"North Dakota","39":"Ohio","40":"Oklahoma","41":"Oregon","42":"Pennsylvania","44":"Rhode Island","45":"South Carolina","46":"South Dakota","47":"Tennessee","48":"Texas","49":"Utah","50":"Vermont","51":"Virginia","53":"Washington","54":"West Virginia","55":"Wisconsin","56":"Wyoming"}
d["unit_name"] = d["unit_id"].str[3:].map(US_STATES)
d = d.assign(country="United States", iso3="USA",
             admin_level=1, crop=d["crop"].str.lower().str.strip(),
             area_ha=d["area_acres"] * ACRE, source="usda_census_qs")
frames.append(d[["country", "iso3", "unit_id", "unit_name", "admin_level",
                 "year", "crop", "area_ha", "source"]])
print("usda", len(d))

# ---- 6. IBGE PAM state (UF) level ------------------------------------------
UF = ["Acre", "Alagoas", "Amapa", "Amazonas", "Bahia", "Ceara", "Distrito Federal",
      "Espirito Santo", "Goias", "Maranhao", "Mato Grosso", "Mato Grosso do Sul",
      "Minas Gerais", "Para", "Paraiba", "Parana", "Pernambuco", "Piaui",
      "Rio de Janeiro", "Rio Grande do Norte", "Rio Grande do Sul",
      "Rondonia", "Roraima", "Santa Catarina", "Sao Paulo", "Sergipe", "Tocantins"]
rows = []
with zipfile.ZipFile(RAW / "ibge_pam_2016.zip") as z:
    for n in z.namelist():
        if not n.endswith(".xls") or n.endswith("Brasil.xls"):
            continue
        uf = Path(n).stem.replace("Tab15_", "")
        if uf not in UF:
            continue
        t = pd.read_excel(z.open(n), header=None)
        for i in range(5, len(t)):
            prod, harv = t.iloc[i, 0], pd.to_numeric(t.iloc[i, 2], errors="coerce")
            if not isinstance(prod, str) or prod.strip() == "" or pd.isna(harv):
                continue
            if prod.strip().upper() in ("TOTAL",):
                continue
            rows.append((uf, 2016, prod.strip().lower(), harv))
with zipfile.ZipFile(RAW / "ibge_pam_uf_2002.zip") as z:
    for n in z.namelist():
        if not n.endswith(".xls") or "Tab_01" in n:
            continue
        t = pd.read_excel(z.open(n), header=None)
        crop = None
        for i in range(5, len(t)):
            v0 = t.iloc[i, 0]
            if crop is None and isinstance(v0, str) and pd.isna(t.iloc[i, 1]):
                crop = v0
                continue
            uf = v0.strip() if isinstance(v0, str) else None
            harv = pd.to_numeric(t.iloc[i, 2], errors="coerce")
            if uf in UF and crop is not None and not pd.isna(harv):
                rows.append((uf, 2002, crop.strip().lower(), harv))
br = pd.DataFrame(rows, columns=["unit_name", "year", "crop", "area_ha"])
br = br.assign(country="Brazil", iso3="BRA", unit_id="BR:" + br["unit_name"],
               admin_level=1, source="ibge_pam")
frames.append(br[["country", "iso3", "unit_id", "unit_name", "admin_level",
                  "year", "crop", "area_ha", "source"]])
print("ibge", len(br))

# ---- unify + write ----------------------------------------------------------
m = pd.concat(frames, ignore_index=True)
m["year"] = m["year"].astype(int)
m.to_parquet(OUT / "admin_crop_observation_matrix.parquet", index=False)

cov = (m.groupby(["source", "country", "unit_id", "unit_name", "admin_level"])
        .agg(years_observed=("year", "nunique"), year_min=("year", "min"),
             year_max=("year", "max"), crop_rows=("crop", "count"),
             crops=("crop", "nunique"), total_area_ha=("area_ha", "sum"))
        .reset_index())
cov["has_2plus_vintages"] = cov["years_observed"] >= 2
cov.to_csv(OUT / "admin_unit_coverage.csv", index=False)
print("units:", cov["unit_id"].nunique(), "countries:", cov["country"].nunique(),
      "rows:", len(m))
print(cov.groupby("source")["unit_id"].nunique())
