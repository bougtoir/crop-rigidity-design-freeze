#!/usr/bin/env python3
"""V3 lock — spatial scale harmonization (outcome-free).

Assigns every candidate unit a source-native geographic level, freezes one
primary subnational scale, audits scale heterogeneity, and writes the
locked primary sample. No outcome variable is used for any decision.
"""
import numpy as np
import pandas as pd
import geopandas as gpd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "SUBNATIONAL_RIGIDITY_DESIGN_FREEZE"
V3 = ROOT / "SUBNATIONAL_RIGIDITY_LOCK_V3"
(V3 / "analysis").mkdir(parents=True, exist_ok=True)
RAW = ROOT / "data" / "raw"

dm = pd.read_csv(ROOT / "SUBNATIONAL_RIGIDITY_FINAL_LOCK" / "analysis"
                 / "final_primary_design_matrix_preoutcome.csv")
xw = pd.read_csv(OUT / "ADMIN_BOUNDARY_CROSSWALK.csv")
src_of = xw.drop_duplicates("unit_id").set_index("unit_id")["source"]

# ---------- level assignment ----------
def level_of(uid, src):
    if uid.startswith("HV1:"):
        return ("humanitarian admin1", "HarvestStat admin_1 aggregation")
    if uid.startswith("HV2:"):
        return ("humanitarian admin2", "HarvestStat fnid")
    if uid.startswith("GADM:"):
        return ("ADM1", "FAO subnational GADM code (_1 suffix)")
    if uid.startswith("US:"):
        return ("ADM1", "US state")
    if uid.startswith("BR:"):
        return ("ADM1", "Brazil UF")
    if uid.startswith("CA:"):
        return ("ADM1", "Canada province/territory")
    # bare NUTS codes: NUTS0=2ch, NUTS1=3ch, NUTS2=4ch; merged codes excluded
    if "_" in uid:
        return ("merged", "Eurostat merged vintage code")
    if len(uid) == 2:
        return ("NUTS0", "Eurostat country level")
    if len(uid) == 3:
        return ("NUTS1", "Eurostat NUTS1")
    if len(uid) == 4:
        return ("NUTS2", "Eurostat NUTS2")
    return ("unknown", "")

rows = []
for _, r in dm.iterrows():
    lv, note = level_of(r.unit_id, src_of.get(r.unit_id, ""))
    rows.append(dict(unit_id=r.unit_id, country=r.country,
                     source=src_of.get(r.unit_id, "unknown"),
                     source_native_level=lv, source_native_level_name=note,
                     reference_admin_level="ADM1_equiv",
                     reference_geometry_id=r.unit_id,
                     parent_country=r.country))
lvl = pd.DataFrame(rows)

# ---------- geometries for area ----------
gadm = gpd.read_file(RAW / "gadm410" / "gadm_410-levels.gpkg", layer="ADM_1",
                     columns=["GID_1"])
gid2geom = dict(zip(gadm["GID_1"], gadm.geometry))
nuts = {}
for lv in (1, 2):
    g = gpd.read_file(RAW / "subnat" / f"nuts2021_l{lv}.geojson")
    nuts.update(dict(zip(g["NUTS_ID"], g.geometry)))
hv = gpd.read_file(RAW / "subnat" / "hvstat_africa_boundary_v1.2.gpkg")
hv["_key"] = ("HV1:" + hv["country_code"].astype(str) + ":"
              + hv["admin_1"].fillna("").astype(str))
hv_units = {}
for k, s in hv[hv["admin_1"].notna()].groupby("_key"):
    hv_units[k] = s.union_all()
for _, r in hv[hv["admin_1"].isna()].iterrows():
    hv_units["HV2:" + r["fnid"]] = r.geometry
gid_of = xw.drop_duplicates("unit_id").set_index("unit_id")["gadm41_gid"]

def geom_of(uid):
    gid = gid_of.get(uid)
    if pd.notna(gid) and gid in gid2geom:
        return gid2geom[gid]
    if uid in hv_units:
        return hv_units[uid]
    return nuts.get(uid)

geoms = {u: geom_of(u) for u in lvl.unit_id}
geo_series = gpd.GeoSeries({u: g for u, g in geoms.items() if g is not None},
                           crs="EPSG:4326").to_crs("EPSG:6933")
area = (geo_series.area / 1e6)
lvl["area_km2"] = lvl.unit_id.map(area)
lvl["has_geometry"] = lvl.unit_id.map({u: g is not None for u, g in geoms.items()})

# ---------- frozen scale ----------
# eligible: genuine first-subnational level (ADM1, humanitarian admin1,
# NUTS2 — the single predeclared NUTS level for Europe matching first-level
# regions for the countries in this sample).
ELIG = {"ADM1", "humanitarian admin1", "NUTS2"}
lvl["harmonization_status"] = np.where(
    lvl.source_native_level.isin(ELIG), "eligible", "excluded_level")

elig = lvl[lvl.harmonization_status == "eligible"]
per_cty = elig.groupby("country").size()
keep_cty = set(per_cty[per_cty >= 2].index)
lvl["harmonization_status"] = np.where(
    lvl.harmonization_status.eq("eligible")
    & ~lvl.country.isin(keep_cty), "excluded_solo_country",
    lvl.harmonization_status)
lvl.to_csv(V3 / "analysis" / "01_UNIT_LEVEL_AUDIT.csv", index=False)

# ---------- scale diagnostics ----------
e = lvl[lvl.harmonization_status == "eligible"]
diag = dict(
    n_eligible=len(e), n_countries=e.country.nunique(),
    median_area_km2=float(e.area_km2.median()),
    area_ratio_max_min=float(e.area_km2.max() / e.area_km2.min()),
    median_units_per_country=float(e.groupby("country").size().median()),
    min_units_per_country=int(e.groupby("country").size().min()),
    countries_one_unit=int((e.groupby("country").size() == 1).sum()))
med_src = e.groupby("source")["area_km2"].median().to_dict()
med_cty = e.groupby("country")["area_km2"].median()
pd.DataFrame([diag]).to_csv(V3 / "analysis" / "spatial_scale_diagnostics.csv",
                            index=False)
med_cty.to_csv(V3 / "analysis" / "median_area_by_country.csv")
print(diag)
print(med_src)
print(lvl.harmonization_status.value_counts())

# ---------- locked sample ----------
sel = dm.merge(e[["unit_id", "area_km2"]], on="unit_id")
sel = sel.dropna(subset=["irr_share_base2000", "mismatch_T", "jsd"])
sel.to_csv(V3 / "analysis" / "PRIMARY_SUBNATIONAL_SAMPLE_LOCKED.csv",
           index=False)
import hashlib
h = hashlib.sha256(open(V3 / "analysis" /
             "PRIMARY_SUBNATIONAL_SAMPLE_LOCKED.csv", "rb").read()).hexdigest()
open(V3 / "analysis" / "PRIMARY_SUBNATIONAL_SAMPLE_LOCKED.sha256", "w").write(
    h + "  PRIMARY_SUBNATIONAL_SAMPLE_LOCKED.csv\n")
print("locked sample:", len(sel), "units,", sel.country.nunique(), "countries")
print(sorted(sel.country.unique()))
print(sel.groupby("country").size().sort_values().head(12).to_string())
