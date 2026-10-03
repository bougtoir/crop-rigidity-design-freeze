#!/usr/bin/env python3
"""Phase 9: irrigation exposure by admin-1 unit.

I2 = SPAM 2010 irrigated harvested area / total harvested area (zonal over unit
geometry). I1 = USDA census reported irrigated acres / harvested acres for US.
I3 (GMIA v5) evaluated for coverage but zonal geometry is the constraint; GMIA
raster not yet persisted -> documented.
Emits analysis/irrigation_source_comparison.csv and adds irr_share columns to
design_matrix_irr.csv.
"""
import re
import numpy as np
import pandas as pd
import geopandas as gpd
import rasterio
from rasterio.features import rasterize
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "SUBNATIONAL_RIGIDITY_DESIGN_FREEZE"
RAW = ROOT / "data" / "raw"

dm = pd.read_csv(OUT / "analysis" / "design_matrix.csv")
xw = pd.read_csv(OUT / "ADMIN_BOUNDARY_CROSSWALK.csv")

# ---------- geometries ----------
geoms = {}   # unit_id -> list of shapely geoms (EPSG:4326)

# GADM ADM_1 for matched units
gadm = gpd.read_file(RAW / "gadm410" / "gadm_410-levels.gpkg", layer="ADM_1",
                     columns=["GID_1"])
gid2geom = dict(zip(gadm["GID_1"], gadm.geometry))

# NUTS 2021
nuts = {}
for lvl in (1, 2):
    f = RAW / "subnat" / f"nuts2021_l{lvl}.geojson"
    g = gpd.read_file(f)
    for _, r in g.iterrows():
        nuts[r["NUTS_ID"]] = r.geometry

# HarvestStat fnid polygons -> admin-1 unit union
hv = gpd.read_file(RAW / "subnat" / "hvstat_africa_boundary_v1.2.gpkg")
hv["_key"] = ("HV1:" + hv["country_code"].astype(str) + ":"
              + hv["admin_1"].fillna("").astype(str))
hv_units = {k: list(s.geometry) for k, s in hv[hv["admin_1"].notna()].groupby("_key")}
for _, r in hv[hv["admin_1"].isna()].iterrows():
    hv_units["HV2:" + r["fnid"]] = [r.geometry]

for _, u in xw.iterrows():
    uid = u.unit_id
    if pd.notna(u.gadm41_gid) and u.gadm41_gid in gid2geom:
        geoms[uid] = [gid2geom[u.gadm41_gid]]
    elif uid in hv_units:
        geoms[uid] = hv_units[uid]
    elif uid in nuts:
        geoms[uid] = [nuts[uid]]

print("units with geometry:", len(geoms), "of", len(dm))

# ---------- rasterize to SPAM grid ----------
tif_dir = RAW / "mapspam" / "spam2010_H"
files = sorted(tif_dir.glob("*_A.tif"))
ref = rasterio.open(files[0])
shape, transform = ref.shape, ref.transform
ref.close()

uids = list(geoms)
uid_idx = {u: i + 1 for i, u in enumerate(uids)}
zone = np.zeros(shape, dtype=np.int32)
for u, glist in geoms.items():
    zone |= rasterize([(g, uid_idx[u]) for g in glist], out_shape=shape,
                      transform=transform, all_touched=False, dtype=np.int32)
print("cells zoned:", int((zone > 0).sum()))

n = len(uids)
totA = np.zeros(n + 1, dtype=np.float64)
totI = np.zeros(n + 1, dtype=np.float64)
for f in files:
    crop = f.stem.split("_")[-2]
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
    del a

irr = pd.DataFrame({"unit_id": uids,
                    "spam_A_ha": totA[1:n + 1],
                    "spam_I_ha": totI[1:n + 1]})
irr["irr_share_spam"] = (irr.spam_I_ha / irr.spam_A_ha.replace(0, np.nan)).clip(0, 1)

# ---------- USDA reported irrigation (I1) ----------
def usda_irrigated(fn):
    import gzip
    rows = {}
    with gzip.open(fn, "rt") as f:
        h = f.readline().rstrip("\n").split("\t")
        i = {c: h.index(c) for c in
             ["COMMODITY_DESC", "PRODN_PRACTICE_DESC", "STATISTICCAT_DESC",
              "AGG_LEVEL_DESC", "STATE_FIPS_CODE", "VALUE", "DOMAIN_DESC",
              "DOMAINCAT_DESC", "YEAR"]}
        for line in f:
            p = line.rstrip("\n").split("\t")
            if p[i["AGG_LEVEL_DESC"]] != "COUNTY":
                continue
            if p[i["COMMODITY_DESC"]] != "AG LAND":
                continue
            if p[i["PRODN_PRACTICE_DESC"]] != "IRRIGATED":
                continue
            if p[i["STATISTICCAT_DESC"]] != "AREA":
                continue
            if p[i["DOMAIN_DESC"]] != "TOTAL" or                p[i["DOMAINCAT_DESC"]] != "NOT SPECIFIED":
                continue
            v = p[i["VALUE"]].replace(",", "")
            try:
                v = float(v)
            except ValueError:
                continue
            k = "US:" + p[i["STATE_FIPS_CODE"]].zfill(2)
            rows[k] = rows.get(k, 0) + v
    return rows

ir2002 = usda_irrigated(RAW / "subnat" / "qs.census2002.txt.gz")
dm2 = dm.merge(irr[["unit_id", "spam_A_ha", "spam_I_ha", "irr_share_spam"]],
               on="unit_id", how="left")
us_area = dm2[dm2.source == "usda_census_qs"].set_index("unit_id")
us_area = us_area.copy()
dm2["irr_share_reported"] = np.nan
dm2.loc[dm2.source == "usda_census_qs", "irr_share_reported"] = (
    dm2.loc[dm2.source == "usda_census_qs", "unit_id"].map(
        lambda k: ir2002.get(k, np.nan)) /
    dm2.loc[dm2.source == "usda_census_qs", "area_baseline"].replace(0, np.nan) * 0.404685642)
dm2["irr_share_reported"] = dm2["irr_share_reported"].clip(0, 1)
dm2["irr_share"] = dm2["irr_share_spam"].fillna(dm2["irr_share_reported"])
dm2.to_csv(OUT / "analysis" / "design_matrix_irr.csv", index=False)

comp = pd.DataFrame(dict(
    source_metric=["I1_usda_reported", "I2_spam_zonal"],
    coverage_units=[int(dm2.irr_share_reported.notna().sum()),
                    int(dm2.irr_share_spam.notna().sum())],
    mean=[dm2.irr_share_reported.mean(), dm2.irr_share_spam.mean()],
    sd=[dm2.irr_share_reported.std(), dm2.irr_share_spam.std()]))
sub = dm2.dropna(subset=["irr_share_reported", "irr_share_spam"])
comp["corr_with_other_source"] = [sub.irr_share_reported.corr(sub.irr_share_spam),
                                  np.nan]
comp.to_csv(OUT / "analysis" / "irrigation_source_comparison.csv", index=False)
print(comp.to_string())
print(dm2.irr_share.describe())
