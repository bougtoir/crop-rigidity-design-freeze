#!/usr/bin/env python3
"""11_final_lock_inputs.py — final lock phase inputs (NO beta3 anywhere).

Frozen temporal ladder (2002 boundary):
  legacy crop mix      1981-2001
  footprint            SPAM2000 avg(1999-2001)
  climate baseline     1984-2001 (NASA POWER monthly coverage)
  exposure             2002-2020
  outcome              crop mix 2002-2020
Old ladder (1981-2000/2001-2020) retained as predefined sensitivity.

Outputs under CROP_RIGIDITY_FINAL_LOCK/:
  analysis/temporal_boundary_diagnostics.csv
  analysis/cropmix_diagnostics_v2.csv
  CROP_CALENDAR_CROSSWALK.csv
  analysis/calendar_vs_thermal_mismatch.csv
  analysis/mismatch_diagnostics_v3.csv
  analysis/primary_sample_flow.csv (also copied as 01_PRIMARY_SAMPLE_FLOW.csv)
  analysis/primary_sample_preoutcome.csv
"""
import gzip
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.covariance import LedoitWolf

ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "CROP_RIGIDITY_FINAL_LOCK"
AN = PKG / "analysis"
AN.mkdir(parents=True, exist_ok=True)
RAW = ROOT / "data" / "raw"
REPAIR = ROOT / "CROP_RIGIDITY_PREANALYSIS_REPAIR"

LEGACY = (1981, 2001)
OUTCOME = (2002, 2020)
BASE = (1984, 2001)
EXPO = (2002, 2020)

df = pd.read_feather(RAW / "faostat_qcl_2026-02-25.feather")
ha = df[(df.element == "Area harvested") & (df.value > 0)]
audit = pd.read_csv(REPAIR / "FAOSTAT_CROP_ITEM_AUDIT.csv")
keep = set(audit.loc[audit.include_primary == 1, "item_name"])
ha = ha[ha["item"].isin(keep)][["country", "year", "item", "value"]]

xw = pd.read_csv(REPAIR / "COUNTRY_REGION_CROSSWALK.csv")
sxw = pd.read_csv(REPAIR / "SPAM_FAOSTAT_CROSSWALK.csv")
fc = pd.read_csv(REPAIR / "analysis" / "footprint_cells.csv")
name2spam = dict(zip(sxw.item_name, sxw.spam_crop))
iso_of = dict(zip(xw.faostat_country, xw.iso3))
region_of = dict(zip(xw.iso3, xw.region))
sub_of = dict(zip(xw.iso3, xw.subregion))

def shares(d):
    s = d.groupby(["country", "item"], observed=True)["value"].mean().reset_index()
    s["share"] = s.value / s.groupby("country", observed=True).value.transform("sum")
    return s

def js_distance(p, q):
    m = 0.5 * (p + q)
    klp = np.where(p > 0, p * np.log(p / m), 0).sum()
    klq = np.where(q > 0, q * np.log(q / m), 0).sum()
    return float(np.sqrt(0.5 * klp + 0.5 * klq))

def cropmix(legacy, outcome):
    recs = []
    for c, g in ha.groupby("country", observed=True):
        gl = g[(g.year >= legacy[0]) & (g.year <= legacy[1])]
        go = g[(g.year >= outcome[0]) & (g.year <= outcome[1])]
        if gl.year.nunique() < 10 or go.year.nunique() < 10:
            continue
        sl, so = shares(gl), shares(go)
        if sl.item.nunique() < 4 or so.item.nunique() < 4:
            continue
        p = sl.set_index("item")["share"]
        q = so.set_index("item")["share"]
        idx = sorted(set(p.index) | set(q.index))
        p, q = p.reindex(idx, fill_value=0.), q.reindex(idx, fill_value=0.)
        recs.append(dict(country=c, n_crops=sl.item.nunique(),
                         hhi=float((p**2).sum()),
                         dominant_crop=p.idxmax(),
                         jsd=js_distance(p.values, q.values),
                         delta_hhi=float((q**2).sum() - (p**2).sum())))
    return pd.DataFrame(recs)

old = pd.read_csv(REPAIR / "analysis" / "corrected_cropmix_diagnostics.csv")
new = cropmix(LEGACY, OUTCOME)
tb = new.merge(old[["country", "hhi", "jsd", "dominant_crop"]],
               on="country", suffixes=("_v2", "_v1"))
tb["delta_hhi_shift"] = tb.hhi_v2 - tb.hhi_v1
tb["delta_jsd_shift"] = tb.jsd_v2 - tb.jsd_v1
tb["dominant_changed"] = (tb.dominant_crop_v2 != tb.dominant_crop_v1).astype(int)
tb[["country", "hhi_v2", "hhi_v1", "delta_hhi_shift",
    "jsd_v2", "jsd_v1", "delta_jsd_shift",
    "dominant_crop_v2", "dominant_crop_v1", "dominant_changed"]
   ].to_csv(AN / "temporal_boundary_diagnostics.csv", index=False)
new.to_csv(AN / "cropmix_diagnostics_v2.csv", index=False)
print("cropmix v2:", len(new),
      "| median dHHI", round(tb.delta_hhi_shift.median(), 5),
      "dJSD", round(tb.delta_jsd_shift.median(), 5),
      "| dominant changed:", int(tb.dominant_changed.sum()), "/", len(tb))

# ---------------------------------------------------------------- MIRCA CCC
def months_of(s, e):
    if s <= e:
        return set(range(int(s), int(e) + 1))
    return set(range(int(s), 13)) | set(range(1, int(e) + 1))

def parse_ccc(path):
    cal = {}  # unit -> cropclass -> set(months)
    with gzip.open(path, "rt") as f:
        for line in f:
            t = line.split()
            if len(t) < 3 or not t[0].lstrip("-").isdigit():
                continue
            unit, cls, nsc = int(t[0]), int(t[1]), int(t[2])
            mm = set()
            for k in range(min(nsc, 5)):
                j = 3 + k * 3
                if j + 2 < len(t) and t[j] not in {"", "NA"}:
                    try:
                        if float(t[j]) > 0:
                            mm |= months_of(float(t[j+1]), float(t[j+2]))
                    except ValueError:
                        pass
            if mm:
                cal.setdefault(unit, {}).setdefault(cls, set()).update(mm)
    return cal

ccc_dir = RAW / "mirca" / "condensed_cropping_calendars"
cal_r = parse_ccc(ccc_dir / "cropping_calendar_rainfed.txt.gz")
cal_i = parse_ccc(ccc_dir / "cropping_calendar_irrigated.txt.gz")
cal = {}
for src in (cal_r, cal_i):
    for u, cls in src.items():
        for c, mm in cls.items():
            cal.setdefault(u, {}).setdefault(c, set()).update(mm)
print("calendar units:", len(cal))

# SPAM class -> MIRCA crop classes (union of seasons across classes)
MIRCA = {1: "wheat", 2: "maize", 3: "rice", 4: "barley", 5: "rye",
         6: "millet", 7: "sorghum", 8: "soybean", 9: "sunflower",
         10: "potato", 11: "cassava", 12: "sugar cane", 13: "sugar beet",
         14: "oil palm", 15: "rapeseed/canola", 16: "groundnuts",
         17: "pulses", 18: "citrus", 19: "date palm", 20: "grapes/vine",
         21: "cotton", 22: "cocoa", 23: "coffee", 24: "others perennial",
         25: "managed grassland", 26: "others annual"}
SPAM2MIRCA = {
    "WHEA": [1], "MAIZ": [2], "RICE": [3], "BARL": [4], "MILL": [6],
    "SORG": [7], "SOYB": [8], "POTA": [10], "CASS": [11], "SUGC": [12],
    "SUGB": [13], "OPUL": [17], "BEAN": [17], "GROU": [16], "COTT": [21],
    "COFF": [23], "SWPY": [26], "BANP": [26], "OFIB": [26],
    "OOIL": [8, 9, 14, 15, 24], "OTHE": [24, 26],
}
cx = []
for sp, cls in SPAM2MIRCA.items():
    cx.append(dict(spam_crop=sp, mirca_classes=";".join(map(str, cls)),
                   mirca_names=";".join(MIRCA[c] for c in cls),
                   calendar_source="MIRCA2000 v1.1 condensed cropping calendars (rainfed+irrigated union)",
                   status="mapped"))
pd.DataFrame(cx).to_csv(PKG / "CROP_CALENDAR_CROSSWALK.csv", index=False)

# unit_code asc grid -> lookup
asc = RAW / "mirca" / "unit_code_grid" / "unit_code.asc"
if not asc.exists():
    import zipfile
    with zipfile.ZipFile(RAW / "mirca" / "unit_code_grid.zip") as zf:
        zf.extract("unit_code_grid/unit_code.asc.gz", RAW / "mirca")
        import shutil
        src = RAW / "mirca" / "unit_code_grid" / "unit_code.asc.gz"
        with gzip.open(src, "rb") as fi, open(asc, "wb") as fo:
            shutil.copyfileobj(fi, fo)
header = {}
grid_rows = []
with open(asc) as f:
    for _ in range(6):
        k, v = f.readline().split()
        header[k.lower()] = float(v)
    grid = np.loadtxt(f)
CS = header["cellsize"]

def unit_at(lon, lat):
    col = int((lon + 180.0) / CS)
    row = int((90.0 - lat) / CS)
    col = min(max(col, 0), grid.shape[1] - 1)
    row = min(max(row, 0), grid.shape[0] - 1)
    if grid[row, col] != -9999:
        return int(grid[row, col])
    for rad in (2, 4, 8, 16):
        vals = grid[max(0, row-rad):row+rad+1, max(0, col-rad):col+rad+1]
        ok = vals[vals != -9999]
        if ok.size:
            u, c = np.unique(ok.astype(int), return_counts=True)
            return int(u[c.argmax()])
    return -9999

# cell -> unit map for all footprint cells
allcells = set()
for j in fc.cells_json:
    allcells.update(map(tuple, json.loads(j)))
unit_cache = {c: unit_at(*c) for c in allcells}
print("cells mapped:", sum(1 for v in unit_cache.values() if v != -9999),
      "/", len(allcells))

# ---------------------------------------------------------------- climate
def load_climate(iso):
    p = RAW / "power" / f"{iso}.parquet"
    if not p.exists():
        return None
    d = pd.read_parquet(p)
    d["lon"] = d.lon.round(3); d["lat"] = d.lat.round(3)
    d["year"] = (d.ym // 100).astype(int)
    d["month"] = (d.ym % 100).astype(int)
    return d[(d.month >= 1) & (d.month <= 12)]

_CLIM = {}
def clim_of(iso):
    if iso not in _CLIM:
        _CLIM[iso] = load_climate(iso)
    return _CLIM[iso]

def seasonal(d, months_by_cell, yr):
    dd = d[(d.year >= yr[0]) & (d.year <= yr[1])].copy()
    dd["key"] = list(zip(dd.lon, dd.lat))
    keep_mask = [m in months_by_cell.get(k, set()) for m, k in zip(dd.month, dd.key)]
    dd = dd[keep_mask]
    return dd.groupby(["lon", "lat", "year"]).agg(
        t=("t2m", "mean"), p=("prec", "sum")).reset_index()

def thermal_months(d, yr=BASE):
    base = d[(d.year >= yr[0]) & (d.year <= yr[1])]
    clim = base.groupby(["lon", "lat", "month"])["t2m"].mean().reset_index()
    return clim[clim.t2m > 5].groupby(["lon", "lat"])["month"].apply(set).to_dict()

def calendar_months(cells, crop_classes):
    out = {}
    for cell in cells:
        u = unit_cache.get(cell, -9999)
        mm = set()
        for c in crop_classes:
            mm |= cal.get(u, {}).get(c, set())
        if mm:
            out[cell] = mm
    return out

def mahalanobis(b, e):
    X = b[["t", "p"]].values
    cov = LedoitWolf().fit(X)
    S = cov.covariance_
    diff = e[["t", "p"]].values.mean(0) - X.mean(0)
    try:
        D = float(np.sqrt(diff @ np.linalg.solve(S, diff)))
        return D, float(np.linalg.cond(S)), float(np.linalg.det(S)), float(cov.shrinkage_)
    except np.linalg.LinAlgError:
        return np.nan, np.inf, 0.0, float(cov.shrinkage_)

def mismatch_for(iso, crop, kind):
    """kind: 'thermal' or 'calendar'"""
    rows = fc[(fc.iso3 == iso) & (fc.spam_crop == crop)]
    if rows.empty:
        return None
    cells = set()
    for j in rows.cells_json:
        cells.update(map(tuple, json.loads(j)))
    d = clim_of(iso)
    if d is None:
        return None
    have = set(zip(d.lon, d.lat))
    cells &= have
    if not cells:
        return None
    if kind == "thermal":
        mbc = {k: v for k, v in thermal_months(d).items() if k in cells}
    else:
        mbc = calendar_months(cells, SPAM2MIRCA.get(crop, []))
    mbc = {k: v for k, v in mbc.items() if v}
    if not mbc:
        return dict(mismatch=np.nan, n_cells=0, cond=np.nan, det=np.nan,
                    shrinkage=np.nan, reg="no season months")
    b = seasonal(d, mbc, BASE)
    e = seasonal(d, mbc, EXPO)
    if len(b) < 10 or len(e) < 10:
        return dict(mismatch=np.nan, n_cells=len(mbc), cond=np.nan, det=np.nan,
                    shrinkage=np.nan, reg="insufficient obs")
    D, cond, det, shr = mahalanobis(b, e)
    return dict(mismatch=D, n_cells=len(mbc), cond=cond, det=det,
                shrinkage=shr, reg="ledoit-wolf common rule")

# ---------------------------------------------------------------- mismatch runs
dom, comp = [], []
for _, r in new.iterrows():
    iso = iso_of.get(r.country)
    if not iso or iso == "none":
        continue
    dcrop = name2spam.get(r.dominant_crop, "none")
    rt = mismatch_for(iso, dcrop, "thermal")
    rc = mismatch_for(iso, dcrop, "calendar")
    comp.append(dict(iso3=iso, country=r.country, spam_crop=dcrop,
                     mismatch_thermal=(rt or {}).get("mismatch", np.nan),
                     mismatch_calendar=(rc or {}).get("mismatch", np.nan),
                     n_cells_thermal=(rt or {}).get("n_cells", np.nan),
                     n_cells_calendar=(rc or {}).get("n_cells", np.nan),
                     reg_calendar=(rc or {}).get("reg", "na")))
    dr = dict(iso3=iso, country=r.country, dominant_crop=r.dominant_crop,
              spam_crop=dcrop,
              mismatch_thermal=(rt or {}).get("mismatch", np.nan),
              mismatch_calendar=(rc or {}).get("mismatch", np.nan),
              n_cells=(rc or rt or {}).get("n_cells", np.nan),
              cond=(rc or {}).get("cond", np.nan),
              det=(rc or {}).get("det", np.nan),
              shrinkage=(rc or {}).get("shrinkage", np.nan),
              reg=(rc or {}).get("reg", "na"))
    dom.append(dr)
compd = pd.DataFrame(comp)
compd.to_csv(AN / "calendar_vs_thermal_mismatch.csv", index=False)
domd = pd.DataFrame(dom)
domd.to_csv(AN / "mismatch_diagnostics_v3.csv", index=False)

ok = compd.dropna(subset=["mismatch_thermal", "mismatch_calendar"])
print("calendar mismatch:", compd.mismatch_calendar.notna().sum(), "/",
      len(compd), "| thermal:", compd.mismatch_thermal.notna().sum(),
      "| corr:", round(ok.mismatch_thermal.corr(ok.mismatch_calendar), 4))
