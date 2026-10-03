#!/usr/bin/env python3
"""V3 final sample: dedup duplicate geographies + recompute exposures.

Dedup rule (predeclared, outcome-blind): when two unit_ids share the same
gadm41_gid within a country they are the same physical admin-1 region —
keep the unit_id whose source contributes more units in that country;
tie -> prefer HV1 (HarvestStat is the SSA-dedicated source and was the
intended representation for those countries in the design freeze).

After dedup, recompute irr_share_base2000 on the surviving units only
(v2 computed it on a zone raster where duplicates overwrote each other)
and recompute mismatch_T for units still missing it (same definitions
as 45_mismatch.py: baseline-weighted |T_end - T_base| over MIRCA
rainfed crop-calendar months, NASA POWER monthly centroids).

Writes PRIMARY_SUBNATIONAL_SAMPLE_LOCKED.csv + .sha256 and
sample_attrition_v3.csv into SUBNATIONAL_RIGIDITY_LOCK_V3/analysis/.
"""
import gzip
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
import geopandas as gpd
import rasterio
from rasterio.features import rasterize

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "SUBNATIONAL_RIGIDITY_DESIGN_FREEZE"
V3 = ROOT / "SUBNATIONAL_RIGIDITY_LOCK_V3"
ANA = V3 / "analysis"
RAW = ROOT / "data" / "raw"
CACHE = RAW / "power_subnat"

lv = pd.read_csv(ANA / "01_UNIT_LEVEL_AUDIT.csv")
elig = set(lv[lv.harmonization_status == "eligible"].unit_id)
dm = pd.read_csv(ROOT / "SUBNATIONAL_RIGIDITY_FINAL_LOCK" / "analysis"
                 / "final_primary_design_matrix_preoutcome.csv")
d = dm[dm.unit_id.isin(elig)].copy()

xw = pd.read_csv(OUT / "ADMIN_BOUNDARY_CROSSWALK.csv")
gid_of = xw.drop_duplicates("unit_id").set_index("unit_id")["gadm41_gid"]

# ---- dedup duplicate geographies ----
d["gadm41_gid"] = d.unit_id.map(gid_of)
d["src"] = d.unit_id.str.split(":").str[0]
d["rank"] = d.unit_id.str.startswith("HV1:").map({True: 0, False: 1})
n_by = d.groupby(["country", "src"]).unit_id.transform("nunique")
d["n_src"] = n_by
d = d.sort_values(["gadm41_gid", "n_src", "rank"],
                  ascending=[True, False, True])
dup_mask = d.gadm41_gid.notna() & d.duplicated(
    ["country", "gadm41_gid"], keep="first")
attr = []
attr.append(dict(stage="eligible_level", n_units=len(d),
                 n_countries=d.country.nunique(),
                 n_dropped=0, reason="audit-eligible levels only"))
d_dedup = d[~dup_mask]
attr.append(dict(stage="dedup_shared_gadm41_gid", n_units=len(d_dedup),
                 n_countries=d_dedup.country.nunique(),
                 n_dropped=int(dup_mask.sum()),
                 reason="same gadm41_gid = same admin-1 region; kept source with "
                        "more units in country, tie->HV1"))
d = d_dedup.copy()

# ---- geometry stack ----
gadm = gpd.read_file(RAW / "gadm410" / "gadm_410-levels.gpkg", layer="ADM_1",
                     columns=["GID_1"])
gid2geom = dict(zip(gadm.GID_1, gadm.geometry))
nuts = {}
for lvl in (1, 2):
    g = gpd.read_file(RAW / "subnat" / f"nuts2021_l{lvl}.geojson")
    nuts.update(dict(zip(g.NUTS_ID, g.geometry)))
# older-code units (e.g. EL11, IE01) are absent from NUTS2021: fall back to
# the NUTS2016 vintage under which those statistics were reported
nuts2016 = {}
for lvl in (1, 2):
    g = gpd.read_file(RAW / "subnat" / f"nuts2016_l{lvl}.geojson")
    nuts2016.update(dict(zip(g.NUTS_ID, g.geometry)))
nuts2010 = {}
for lvl in (1, 2):
    g = gpd.read_file(RAW / "subnat" / f"nuts2010_l{lvl}.geojson")
    nuts2010.update(dict(zip(g.NUTS_ID, g.geometry)))
hv = gpd.read_file(RAW / "subnat" / "hvstat_africa_boundary_v1.2.gpkg")
hv["_key"] = ("HV1:" + hv["country_code"].astype(str) + ":"
              + hv["admin_1"].fillna("").astype(str))
hv_units = {k: s.union_all() for k, s in hv[hv.admin_1.notna()].groupby("_key")}
del gadm


def geom_of(uid):
    gid = gid_of.get(uid)
    if pd.notna(gid) and gid in gid2geom:
        return gid2geom[gid]
    if uid in hv_units:
        return hv_units[uid]
    if uid in nuts:
        return nuts[uid]
    if uid in nuts2016:
        return nuts2016[uid]
    return nuts2010.get(uid)


uids = [u for u in d.unit_id if geom_of(u) is not None]
# ---- irr_share_base2000 on deduped set ----
tif = RAW / "mapspam" / "spam2000_H"
files = sorted(tif.glob("*_A.tif"))
ref = rasterio.open(files[0])
shape, tr = ref.shape, ref.transform
ref.close()
zone = np.zeros(shape, dtype=np.int32)
uid_idx = {u: i + 1 for i, u in enumerate(uids)}
for u in uids:
    zone = np.maximum(zone, rasterize(
        [(geom_of(u), uid_idx[u])], out_shape=shape, transform=tr,
        all_touched=True, dtype=np.int32))
n = len(uids)
totA = np.zeros(n + 1)
totI = np.zeros(n + 1)
for f in files:
    a = rasterio.open(f).read(1)
    if a.shape != shape:
        a = a[:shape[0], :shape[1]]
        if a.shape != shape:
            continue
    a = np.where(np.isfinite(a) & (a > 0), a, 0.0)
    totA += np.bincount(zone.ravel(), weights=a.ravel(), minlength=n + 1)
    fi = tif / f.name.replace("_A.tif", "_I.tif")
    if fi.exists():
        i = rasterio.open(fi).read(1)
        if i.shape != shape:
            i = i[:shape[0], :shape[1]]
            if i.shape != shape:
                continue
        i = np.where(np.isfinite(i) & (i > 0), i, 0.0)
        totI += np.bincount(zone.ravel(), weights=i.ravel(), minlength=n + 1)
irr = {u: (totI[i] / totA[i] if totA[i] > 0 else np.nan)
       for i, u in enumerate(uids)}
d["irr_share_base2000"] = d.unit_id.map(irr).clip(0, 1)
print("irr coverage on deduped:", d.irr_share_base2000.notna().sum(),
      "of", len(d))

# ---- mismatch_T for missing units (same formulas as 45_mismatch.py) ----
names = {}
for line in gzip.open(RAW / "mirca" / "unit_code_grid" / "unit_name.txt.gz",
                      "rt"):
    if line.startswith("Unit"):
        continue
    p = [x for x in line.rstrip("\n").split("\t") if x.strip()]
    if len(p) >= 2:
        names[p[1].split("_")[0]] = names.get(p[1].split("_")[0], []) + [int(p[0])]
MIRCA2CANON = {1: "wheat", 2: "maize", 3: "rice", 4: "barley", 5: "sorghum",
               6: "millet", 7: "other_cereals", 8: "sugarcane", 9: "cassava",
               10: "potato", 11: "soybean", 12: "rapeseed", 13: "cotton",
               14: "tobacco", 15: "dry_beans", 16: "vegetables", 17: "coffee",
               18: "other_annual", 19: "oil_palm", 20: "banana", 21: "citrus",
               22: "grapes", 23: "olive", 24: "other_perennial", 25: "forage",
               26: "other_annual"}
months = {}
for line in gzip.open(RAW / "mirca" / "condensed_cropping_calendars"
                      / "cropping_calendar_rainfed.txt.gz", "rt"):
    if line.startswith(("*", "MIRCA")) or len(line.split()) < 4:
        continue
    p = line.split()
    try:
        uc, cc, nsc = int(p[0]), int(p[1]), int(p[2])
    except ValueError:
        continue
    vals = p[3:]
    can = MIRCA2CANON.get(cc)
    if can is None:
        continue
    for ctry, ucs in names.items():
        if uc in ucs:
            entry = months.setdefault(ctry, {}).setdefault(can, {})
            for j in range(0, 3 * nsc, 3):
                a, s_, e_ = float(vals[j]), int(vals[j + 1]), int(vals[j + 2])
                rng = (range(s_, e_ + 1) if s_ <= e_
                       else list(range(s_, 13)) + list(range(1, e_ + 1)))
                for m_ in rng:
                    entry[m_] = entry.get(m_, 0.0) + a

CTY_MIRCA = {"Tanzania, United Republic of": "Tanzania",
             "Laos": "Lao People's Democratic Republic",
             "Congo, The Democratic Republic of the":
             "Democratic Republic of the Congo",
             "United States": "United States of America",
             "Burkina Faso": "Burkina Faso"}
CTY_MIRCA.update({k: v for k, v in {
    "AT": "Austria", "BE": "Belgium", "BG": "Bulgaria", "CH": "Switzerland",
    "CY": "Cyprus", "CZ": "Czechia", "DE": "Germany", "DK": "Denmark",
    "EE": "Estonia", "EL": "Greece", "ES": "Spain", "FI": "Finland",
    "FR": "France", "HR": "Croatia", "HU": "Hungary", "IE": "Ireland",
    "IS": "Iceland", "IT": "Italy", "LT": "Lithuania", "LU": "Luxembourg",
    "LV": "Latvia", "ME": "Montenegro", "MK": "North Macedonia",
    "MT": "Malta", "NL": "Netherlands", "NO": "Norway", "PL": "Poland",
    "PT": "Portugal", "RO": "Romania", "RS": "Serbia", "SE": "Sweden",
    "SI": "Slovenia", "SK": "Slovakia", "TR": "Turkey", "UK": "United Kingdom",
    "AL": "Albania", "BA": "Bosnia and Herzegovina", "XK": "Kosovo"}.items()})


import urllib.request
from concurrent.futures import ThreadPoolExecutor


def fetch_power(uid, lon, lat):
    f = CACHE / f"{uid.replace('/', '_')}.json"
    if f.exists() and f.stat().st_size > 500:
        return uid, None
    url = ("https://power.larc.nasa.gov/api/temporal/monthly/point?"
           f"parameters=T2M,PRECTOTCORR&community=AG&longitude={lon:.4f}"
           f"&latitude={lat:.4f}&start=1998&end=2024&format=JSON")
    try:
        with urllib.request.urlopen(url, timeout=60) as r:
            f.write_bytes(r.read())
        return uid, "ok"
    except Exception as e:  # noqa: BLE001 - network failures logged below
        return uid, str(e)


need_pre = d[d.mismatch_T.isna()]
todo = []
for u in need_pre.unit_id:
    g = geom_of(u)
    if g is None:
        continue
    c = g.centroid
    if not (CACHE / f"{u.replace('/', '_')}.json").exists():
        todo.append((u, c.x, c.y))
print("POWER fetches:", len(todo))
with ThreadPoolExecutor(max_workers=12) as ex:
    for uid, res in ex.map(lambda t: fetch_power(*t), todo):
        if res not in (None, "ok"):
            print("fetch fail", uid, res)


def power_series(uid):
    f = CACHE / f"{uid.replace('/', '_')}.json"
    if not f.exists():
        return None
    dd = json.loads(f.read_text())
    p = dd["properties"]["parameter"]
    out = {}
    for k, v in p["T2M"].items():
        y, m_ = int(k[:4]), int(k[4:])
        if m_ == 13:
            continue
        out.setdefault(y, {})[m_] = (v, p["PRECTOTCORR"].get(k, np.nan))
    return out


def season_val(series, yrs, mlist, idx):
    v = [series.get(y, {}).get(m_, (np.nan, np.nan))[idx]
         for y in yrs for m_ in mlist]
    v = [x for x in v if np.isfinite(x)]
    return float(np.mean(v)) if v else np.nan


need = d[d.mismatch_T.isna()]
fill = {}
for _, r in need.iterrows():
    uid, b, e = r.unit_id, r.y0, r.y1
    series = power_series(uid)
    if series is None:
        continue
    mcty = CTY_MIRCA.get(r.country, r.country)
    cal = months.get(mcty, {})
    if not cal:
        continue
    b_yrs, e_yrs = range(b - 1, b + 2), range(e - 1, e + 2)
    T0 = T1 = wsum = 0.0
    for can, mm in cal.items():
        mlist = sorted(mm.keys())
        if not mlist:
            continue
        t0 = season_val(series, b_yrs, mlist, 0)
        t1 = season_val(series, e_yrs, mlist, 0)
        if np.isnan(t0) or np.isnan(t1):
            continue
        T0 += t0
        T1 += t1
        wsum += 1
    if wsum:
        fill[uid] = abs(T1 - T0) / wsum
print("mismatch filled for", len(fill), "of", len(need), "missing units")
d["mismatch_T"] = d.mismatch_T.fillna(d.unit_id.map(fill))

# ---- completeness + >=2 units per country ----
before = len(d)
d = d.dropna(subset=["jsd", "irr_share_base2000", "mismatch_T"])
attr.append(dict(stage="complete_exposure_outcome", n_units=len(d),
                 n_countries=d.country.nunique(),
                 n_dropped=before - len(d),
                 reason="jsd, irr_share_base2000, mismatch_T all non-null"))
cnt = d.country.value_counts()
keep = cnt[cnt >= 2].index
attr.append(dict(stage="min2_units_per_country", n_units=len(d[d.country.isin(keep)]),
                 n_countries=len(keep),
                 n_dropped=len(d) - len(d[d.country.isin(keep)]),
                 reason="countries with a single eligible unit excluded "
                        "(no within-country variation)"))
d = d[d.country.isin(keep)].copy()
d = d.drop(columns=["gadm41_gid", "src", "rank", "n_src"], errors="ignore")

out = ANA / "PRIMARY_SUBNATIONAL_SAMPLE_LOCKED.csv"
d.to_csv(out, index=False)
h = hashlib.sha256(out.read_bytes()).hexdigest()
(ANA / "PRIMARY_SUBNATIONAL_SAMPLE_LOCKED.sha256").write_text(
    f"{h}  PRIMARY_SUBNATIONAL_SAMPLE_LOCKED.csv\n")
pd.DataFrame(attr).to_csv(ANA / "sample_attrition_v3.csv", index=False)
print(d.country.value_counts().to_string())
print("FINAL:", len(d), "units,", d.country.nunique(), "countries")
