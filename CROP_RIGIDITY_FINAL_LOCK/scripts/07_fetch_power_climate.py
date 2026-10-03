#!/usr/bin/env python3
"""07_fetch_power_climate.py — fetch NASA POWER monthly T2M/PRECTOTCORR per
country over the union bbox of needed footprint cells (all SPAM crops that
matter per country), save raw JSON + long parquet under data/raw/power/.

Deviation recorded for the repair ledger: NASA POWER monthly series begin
1984-01, so the baseline climate window is 1984-2000 (fully pre-treatment)
rather than 1961-1990. Documented in 00_TEMPORAL_LEAKAGE_REPAIR.md.
"""
import json
import subprocess
import time
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
AN = ROOT / "CROP_RIGIDITY_PREANALYSIS_REPAIR" / "analysis"
RAW = ROOT / "data" / "raw" / "power"
RAW.mkdir(parents=True, exist_ok=True)
(RAW / "json").mkdir(exist_ok=True)
START, END = 1984, 2020
MAX_SPAN = 10.0  # degrees per sub-bbox to bound response size

fc = pd.read_csv(AN / "footprint_cells.csv")
xw = pd.read_csv(ROOT / "CROP_RIGIDITY_PREANALYSIS_REPAIR" /
                 "COUNTRY_REGION_CROSSWALK.csv")
est = set(xw.loc[xw.status == "mapped", "iso3"])

# union of needed cells per country: dominant+portfolio crops -> all crops
need = {}
for iso, g in fc.groupby("iso3"):
    if iso not in est:
        continue
    cells = set()
    for j in g.cells_json:
        cells.update(map(tuple, json.loads(j)))
    need[iso] = cells

def fetch(iso, bbox, param):
    lat_min, lat_max, lon_min, lon_max = bbox
    url = ("https://power.larc.nasa.gov/api/temporal/monthly/regional?"
           f"parameters={param}&community=AG"
           f"&longitude-min={lon_min}&longitude-max={lon_max}"
           f"&latitude-min={lat_min}&latitude-max={lat_max}"
           f"&start={START}&end={END}&format=JSON")
    out = subprocess.run(
        ["curl", "-s", "--retry", "3", "--max-time", "300", url],
        capture_output=True, text=True)
    return out.stdout

rows_meta = []
for i, (iso, cells) in enumerate(sorted(need.items())):
    rawj = RAW / "json" / f"{iso}.json"
    parq = RAW / f"{iso}.parquet"
    if parq.exists() and rawj.exists():
        continue
    lats = [c[1] for c in cells]; lons = [c[0] for c in cells]
    # axis windows covering needed cells: each <=10 deg span, >=2 deg span
    def windows(vals, step):
        vals = sorted(set(vals))
        wins = []
        cov = set()
        for v in vals:
            if v in cov:
                continue
            lo = v
            hi = min(v + step, max(vals))
            if hi - lo < 2.0:
                lo = min(lo, hi - 2.0)
            lo2 = min(lo, v) - 0.5
            hi2 = hi + 0.5
            if hi2 - lo2 > step:
                hi2 = lo2 + step
            wins.append((lo2, hi2))
            cov.update(x for x in vals if lo <= x <= hi)
        return wins
    lat_w = windows(lats, MAX_SPAN)
    lon_w = windows(lons, MAX_SPAN)
    feats = []   # (lon,lat) -> {T2M: {...}, PRECTOTCORR: {...}}
    series = {}
    try:
        for param in ("T2M", "PRECTOTCORR"):
            for (la, la2) in lat_w:
                for (lo, lo2) in lon_w:
                    bbox = (la, la2, lo, lo2)
                    d = None
                    for attempt in range(4):
                        d = json.loads(fetch(iso, bbox, param))
                        if "features" in d:
                            break
                        time.sleep(8 * (attempt + 1))
                    if d is None or "features" not in d:
                        raise RuntimeError(str(d)[:200])
                    for f in d["features"]:
                        lon, lat = f["geometry"]["coordinates"][:2]
                        key = (round(lon, 3), round(lat, 3))
                        series.setdefault(key, {})[param] = \
                            f["properties"]["parameter"][param]
    except Exception as e:
        print(iso, "FAILED", e)
        rows_meta.append(dict(iso3=iso, status="failed", error=str(e)[:200]))
        continue
    rawj.write_text(json.dumps(
        {f"{k[0]},{k[1]}": v for k, v in series.items()}))
    need_cells = {(round(a, 3), round(b, 3)) for a, b in cells}
    recs = []
    for (lon, lat), p in series.items():
        if (lon, lat) not in need_cells:
            continue
        for ym, t in p.get("T2M", {}).items():
            recs.append(dict(iso3=iso, lon=lon, lat=lat, ym=int(ym),
                             t2m=t, prec=p.get("PRECTOTCORR", {}).get(ym)))
    pd.DataFrame(recs).to_parquet(parq)
    rows_meta.append(dict(iso3=iso, status="ok", n_cells=len({(r['lon'], r['lat']) for r in recs}),
                          n_months=len(recs)))
    print(i, iso, len(recs))
pd.DataFrame(rows_meta).to_csv(AN / "power_fetch_log.csv", index=False)
print("done")
