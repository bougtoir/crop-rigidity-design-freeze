#!/usr/bin/env python3
"""21_aux_mismatch.py — auxiliary crop-calendar mismatches for
pre-registered robustness and falsification rows.

Computes, with the SAME pipeline as the frozen primary (MIRCA CCC months,
SPAM2000 footprints, POWER monthly climate, Ledoit-Wolf common rule),
the variants needed downstream. No interaction is estimated here.

Outputs (analysis/aux_mismatches.csv): iso3 x variant -> mismatch
  primary          BASE 1984-2001 / EXPO 2002-2020 (== lock; sanity)
  old_ladder       BASE 1984-2000 / EXPO 2001-2020 (dominant = 1981-2000)
  lagged           BASE 1984-2000 / EXPO 2001-2010 (dominant = 1981-2000)
  pre_treatment    BASE 1984-1990 / EXPO 1991-2000
  future           BASE 1984-2001 / EXPO 2011-2020
Dominant crop is the LEGACY-window dominant of the row's design.
"""
import gzip
import json
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.covariance import LedoitWolf

ROOT = Path(__file__).resolve().parents[1]
LOCK = ROOT / "CROP_RIGIDITY_FINAL_LOCK"
REPAIR = ROOT / "CROP_RIGIDITY_PREANALYSIS_REPAIR"
RAW = ROOT / "data" / "raw"
AN = LOCK / "analysis"

xw = pd.read_csv(REPAIR / "COUNTRY_REGION_CROSSWALK.csv")
sxw = pd.read_csv(REPAIR / "SPAM_FAOSTAT_CROSSWALK.csv")
fc = pd.read_csv(REPAIR / "analysis" / "footprint_cells.csv")
name2spam = dict(zip(sxw.item_name, sxw.spam_crop))
iso_of = dict(zip(xw.faostat_country, xw.iso3))

# ---- MIRCA machinery (same as 11_final_lock_inputs) ------------------------
def months_of(s, e):
    return set(range(int(s), int(e) + 1)) if s <= e else \
        set(range(int(s), 13)) | set(range(1, int(e) + 1))

def parse_ccc(path):
    cal = {}
    with gzip.open(path, "rt") as f:
        for line in f:
            t = line.split()
            if len(t) < 3 or not t[0].lstrip("-").isdigit():
                continue
            u, c, n = int(t[0]), int(t[1]), int(t[2]); mm = set()
            for k in range(min(n, 5)):
                j = 3 + k * 3
                if j + 2 < len(t):
                    try:
                        if float(t[j]) > 0:
                            mm |= months_of(float(t[j+1]), float(t[j+2]))
                    except ValueError:
                        pass
            if mm:
                cal.setdefault(u, {}).setdefault(c, set()).update(mm)
    return cal

cc = RAW / "mirca" / "condensed_cropping_calendars"
cal = parse_ccc(cc / "cropping_calendar_rainfed.txt.gz")
ci = parse_ccc(cc / "cropping_calendar_irrigated.txt.gz")
for u, cls in ci.items():
    for c, mm in cls.items():
        cal.setdefault(u, {}).setdefault(c, set()).update(mm)

hdr = {}
with open(RAW / "mirca" / "unit_code_grid" / "unit_code.asc") as f:
    for _ in range(6):
        k, v = f.readline().split(); hdr[k.lower()] = float(v)
    grid = np.loadtxt(f)
CS = hdr["cellsize"]
def unit_at(lon, lat):
    col = min(max(int((lon + 180) / CS), 0), grid.shape[1] - 1)
    row = min(max(int((90 - lat) / CS), 0), grid.shape[0] - 1)
    if grid[row, col] != -9999:
        return int(grid[row, col])
    for rad in (2, 4, 8, 16):
        vals = grid[max(0, row-rad):row+rad+1, max(0, col-rad):col+rad+1]
        ok = vals[vals != -9999]
        if ok.size:
            u, c = np.unique(ok.astype(int), return_counts=True)
            return int(u[c.argmax()])
    return -9999

allcells = set()
for j in fc.cells_json:
    allcells.update(map(tuple, json.loads(j)))
uc = {c: unit_at(*c) for c in allcells}

SPAM2MIRCA = {"WHEA": [1], "MAIZ": [2], "RICE": [3], "BARL": [4], "MILL": [6],
              "SORG": [7], "SOYB": [8], "POTA": [10], "CASS": [11],
              "SUGC": [12], "SUGB": [13], "OPUL": [17], "BEAN": [17],
              "GROU": [16], "COTT": [21], "COFF": [23], "SWPY": [26],
              "BANP": [26], "OFIB": [26], "OOIL": [8, 9, 14, 15, 24],
              "OTHE": [24, 26]}

_CLIM = {}
def clim(iso):
    if iso not in _CLIM:
        p = RAW / "power" / f"{iso}.parquet"
        d = pd.read_parquet(p) if p.exists() else None
        if d is not None:
            d["lon"] = d.lon.round(3); d["lat"] = d.lat.round(3)
            d["year"] = (d.ym // 100).astype(int)
            d["month"] = (d.ym % 100).astype(int)
            d = d[(d.month >= 1) & (d.month <= 12)]
        _CLIM[iso] = d
    return _CLIM[iso]

def seasonal(d, mbc, yr):
    dd = d[(d.year >= yr[0]) & (d.year <= yr[1])].copy()
    dd["key"] = list(zip(dd.lon, dd.lat))
    dd = dd[[m in mbc.get(k, set()) for m, k in zip(dd.month, dd.key)]]
    return dd.groupby(["lon", "lat", "year"]).agg(
        t=("t2m", "mean"), p=("prec", "sum")).reset_index()

def mmis(iso, crop, base, expo):
    rows = fc[(fc.iso3 == iso) & (fc.spam_crop == crop)]
    if rows.empty: return np.nan
    cells = set()
    for j in rows.cells_json:
        cells.update(map(tuple, json.loads(j)))
    d = clim(iso)
    if d is None: return np.nan
    cells &= set(zip(d.lon, d.lat))
    cls = SPAM2MIRCA.get(crop, [])
    mbc = {}
    for c in cells:
        mm = set()
        for cl in cls:
            mm |= cal.get(uc.get(c, -9999), {}).get(cl, set())
        if mm: mbc[c] = mm
    if not mbc: return np.nan
    b = seasonal(d, mbc, base); e = seasonal(d, mbc, expo)
    if len(b) < 10 or len(e) < 10: return np.nan
    X = b[["t", "p"]].values
    cov = LedoitWolf().fit(X).covariance_
    diff = e[["t", "p"]].values.mean(0) - X.mean(0)
    try:
        return float(np.sqrt(diff @ np.linalg.solve(cov, diff)))
    except np.linalg.LinAlgError:
        return np.nan

# dominant crops: v2 ladder (1981-2001) and old ladder (1981-2000)
new = pd.read_csv(AN / "cropmix_diagnostics_v2.csv")
old = pd.read_csv(REPAIR / "analysis" / "corrected_cropmix_diagnostics.csv")
dom_v2 = dict(zip(new.country, new.dominant_crop))
dom_v1 = dict(zip(old.country, old.dominant_crop))
iso_of_c = {c: iso_of.get(c) for c in set(list(dom_v2) + list(dom_v1))}

rows = []
seen = set()
def emit(iso, variant, m):
    if (iso, variant) not in seen:
        rows.append(dict(iso3=iso, variant=variant, mismatch=m))
        seen.add((iso, variant))

for cname, iso in iso_of_c.items():
    if not iso or iso == "none":
        continue
    d2 = name2spam.get(dom_v2.get(cname, ""), "none")
    d1 = name2spam.get(dom_v1.get(cname, ""), "none")
    emit(iso, "primary", mmis(iso, d2, (1984, 2001), (2002, 2020)))
    emit(iso, "old_ladder", mmis(iso, d1, (1984, 2000), (2001, 2020)))
    emit(iso, "lagged", mmis(iso, d1, (1984, 2000), (2001, 2010)))
    emit(iso, "pre_treatment", mmis(iso, d2, (1984, 1990), (1991, 2000)))
    emit(iso, "future", mmis(iso, d2, (1984, 2001), (2011, 2020)))

out = pd.DataFrame(rows)
out.to_csv(AN.parents[0] / "analysis" / "aux_mismatches.csv"
           if (AN.parents[0] / "analysis").exists() else
           ROOT / "CROP_RIGIDITY_PRIMARY_RESULTS" / "analysis" / "aux_mismatches.csv",
           index=False)
print(out.groupby("variant").mismatch.apply(lambda s: s.notna().sum()))
