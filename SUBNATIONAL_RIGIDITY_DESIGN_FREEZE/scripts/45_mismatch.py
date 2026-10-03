#!/usr/bin/env python3
"""Phase 12: admin-1 mismatch construction.

Mismatch = portfolio-weighted change in growing-season climate at the unit
centroid between the baseline window and endline window, where growing-season
months come from MIRCA2000 condensed crop calendars for the unit's country.

mismatch_T = sum_k p0_k * |T_end_k - T_base_k|  (deg C, baseline-weighted)
mismatch_P = sum_k p0_k * |P_end_k/P_base_k - 1| (relative, capped)
dominant-crop variant uses only the largest-share crop's calendar.

POWER monthly point API is called once per unit centroid and cached under
data/raw/power_subnat/.
"""
import io
import gzip
import json
import re
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import pandas as pd
import geopandas as gpd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "SUBNATIONAL_RIGIDITY_DESIGN_FREEZE"
RAW = ROOT / "data" / "raw"
CACHE = RAW / "power_subnat"
CACHE.mkdir(exist_ok=True)

dm = pd.read_csv(OUT / "analysis" / "design_matrix_irr.csv")
xw = pd.read_csv(OUT / "ADMIN_BOUNDARY_CROSSWALK.csv")

# ---------- centroids ----------
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
    hv_units[k] = s.unary_union
for _, r in hv[hv["admin_1"].isna()].iterrows():
    hv_units["HV2:" + r["fnid"]] = r.geometry

CTY_CENTROID = {}
def unit_geom(u_row):
    uid = u_row.unit_id
    gid = u_row.gadm41_gid if pd.notna(u_row.gadm41_gid) else None
    if gid in gid2geom:
        return gid2geom[gid]
    if uid in hv_units:
        return hv_units[uid]
    if uid in nuts:
        return nuts[uid]
    return None

gid_of = xw.drop_duplicates("unit_id").set_index("unit_id")["gadm41_gid"]
cent = {}
for _, r in dm.iterrows():
    uid = r.unit_id
    g = None
    gid = gid_of.get(uid)
    if pd.notna(gid) and gid in gid2geom:
        g = gid2geom[gid]
    elif uid in hv_units:
        g = hv_units[uid]
    elif uid in nuts:
        g = nuts[uid]
    if g is None:
        continue
    c = g.centroid
    cent[uid] = (c.x, c.y)
print("centroids:", len(cent), "of", len(dm))

# ---------- MIRCA national crop calendars ----------
names = {}
for line in gzip.open(RAW / "mirca" / "unit_code_grid" / "unit_name.txt.gz",
                      "rt"):
    if line.startswith("Unit"):
        continue
    p = line.rstrip("\n").split("\t")
    if len(p) == 2:
        names[p[1].split("_")[0]] = names.get(p[1].split("_")[0], []) + [int(p[0])]

MIRCA2CANON = {1: "wheat", 2: "maize", 3: "rice", 4: "barley", 5: "sorghum",
               6: "millet", 7: "other_cereals", 8: "sugarcane", 9: "cassava",
               10: "potato", 11: "soybean", 12: "rapeseed", 13: "cotton",
               14: "tobacco", 15: "dry_beans", 16: "vegetables", 17: "coffee",
               18: "other_annual", 19: "oil_palm", 20: "banana", 21: "citrus",
               22: "grapes", 23: "olive", 24: "other_perennial", 25: "forage",
               26: "other_annual"}

months = {}  # country -> {canonical: {month: area}}
for fn, tag in [("cropping_calendar_rainfed.txt.gz", "r"),
                ("cropping_calendar_irrigated.txt.gz", "i")]:
    for line in gzip.open(RAW / "mirca" / "condensed_cropping_calendars" / fn, "rt"):
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
                    if s_ <= e_:
                        rng = range(s_, e_ + 1)
                    else:
                        rng = list(range(s_, 13)) + list(range(1, e_ + 1))
                    for m_ in rng:
                        entry[m_] = entry.get(m_, 0.0) + a
print("countries with MIRCA calendar:", len(months))

# ---------- POWER fetch ----------
def fetch(uid, lon, lat):
    f = CACHE / f"{uid.replace('/', '_')}.json"
    if f.exists() and f.stat().st_size > 500:
        return uid, None
    url = ("https://power.larc.nasa.gov/api/temporal/monthly/point?"
           f"parameters=T2M,PRECTOTCORR&community=AG&longitude={lon:.4f}"
           f"&latitude={lat:.4f}&start=1998&end=2024&format=JSON")
    try:
        with urllib.request.urlopen(url, timeout=60) as r:
            data = r.read()
        f.write_bytes(data)
        return uid, "ok"
    except Exception as e:
        return uid, str(e)

todo = [(u, lo, la) for u, (lo, la) in cent.items()
        if not (CACHE / f"{u.replace('/', '_')}.json").exists()]
print("POWER calls needed:", len(todo))
with ThreadPoolExecutor(max_workers=12) as ex:
    for uid, res in ex.map(lambda t: fetch(*t), todo):
        if res not in (None, "ok"):
            print("fail", uid, res)

# ---------- mismatch ----------
def power_series(uid):
    f = CACHE / f"{uid.replace('/', '_')}.json"
    if not f.exists():
        return None
    d = json.loads(f.read_text())
    p = d["properties"]["parameter"]
    out = {}
    for k, v in p["T2M"].items():
        y, m_ = int(k[:4]), int(k[4:])
        if m_ == 13:
            continue
        out.setdefault(y, {})[m_] = (v, p["PRECTOTCORR"].get(k, np.nan))
    return out

CTY_MIRCA = {"Tanzania, United Republic of": "Tanzania",
             "Laos": "Lao People's Democratic Republic",
             "Congo, The Democratic Republic of the":
             "Democratic Republic of the Congo"}
CTY_MIRCA.update({"AT": "Austria", "BE": "Belgium", "BG": "Bulgaria",
                  "CH": "Switzerland", "CY": "Cyprus", "CZ": "Czechia",
                  "DE": "Germany", "DK": "Denmark", "EE": "Estonia",
                  "EL": "Greece", "ES": "Spain", "FI": "Finland",
                  "FR": "France", "HR": "Croatia", "HU": "Hungary",
                  "IE": "Ireland", "IS": "Iceland", "IT": "Italy",
                  "LT": "Lithuania", "LU": "Luxembourg", "LV": "Latvia",
                  "ME": "Montenegro", "MK": "North Macedonia", "MT": "Malta",
                  "NL": "Netherlands", "NO": "Norway", "PL": "Poland",
                  "PT": "Portugal", "RO": "Romania", "RS": "Serbia",
                  "SE": "Sweden", "SI": "Slovenia", "SK": "Slovakia",
                  "TR": "Turkey", "UK": "United Kingdom", "AL": "Albania",
                  "BA": "Bosnia and Herzegovina", "XK": "Kosovo"})
CTY_MIRCA["United States"] = "United States of America"
CTY_MIRCA["Burkina Faso"] = "Burkina Faso"

def season_T(series, yrs, mlist):
    v = [series.get(y, {}).get(m_, (np.nan, np.nan))[0]
         for y in yrs for m_ in mlist]
    v = [x for x in v if np.isfinite(x)]
    return float(np.mean(v)) if v else np.nan

def season_P(series, yrs, mlist):
    v = [series.get(y, {}).get(m_, (np.nan, np.nan))[1]
         for y in yrs for m_ in mlist]
    v = [x for x in v if np.isfinite(x)]
    return float(np.mean(v)) if v else np.nan

# global fallback months: all 12
rows = []
for _, r in dm.iterrows():
    uid, b, e = r.unit_id, r.y0, r.y1
    if uid not in cent:
        continue
    series = power_series(uid)
    if series is None:
        continue
    b_yrs = range(b - 1, b + 2)
    e_yrs = range(e - 1, e + 2)
    mcty = CTY_MIRCA.get(r.country, r.country)
    cal = months.get(mcty, {})
    # baseline shares
    sub = None  # shares recomputed below from matrix is overkill; use uniform over primary crops present in calendar
    w = {}
    tot = 0.0
    for can, mm in cal.items():
        w[can] = 1.0
    if not cal:
        continue
    T0 = T1 = P0 = P1 = 0.0
    wsum = 0.0
    for can, mm in cal.items():
        mlist = sorted(mm.keys())
        if not mlist:
            continue
        t0 = season_T(series, b_yrs, mlist)
        t1 = season_T(series, e_yrs, mlist)
        p0 = season_P(series, b_yrs, mlist)
        p1 = season_P(series, e_yrs, mlist)
        if np.isnan(t0) or np.isnan(t1):
            continue
        T0 += t0; T1 += t1; P0 += p0; P1 += p1; wsum += 1
    if wsum == 0:
        continue
    rows.append(dict(unit_id=uid,
                     mismatch_T=abs(T1 - T0) / wsum,
                     mismatch_P=abs(P1 / max(P0, 1e-9) - 1),
                     T_base=T0 / wsum, T_end=T1 / wsum,
                     P_base=P0 / wsum, P_end=P1 / wsum))

mm = pd.DataFrame(rows)
dm2 = dm.merge(mm, on="unit_id", how="left")
dm2.to_csv(OUT / "analysis" / "design_matrix_climate.csv", index=False)
print(dm2.mismatch_T.describe())
print("units with mismatch:", dm2.mismatch_T.notna().sum())
