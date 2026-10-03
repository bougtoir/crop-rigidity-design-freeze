#!/usr/bin/env python3
"""Phases 6-9, 12, 15: build the locked design matrix.

- Temporal design: baseline = mean shares over years 2000-2005,
  endline = mean over 2016-2022 (sources shorter-ranged use best pair).
- Outcome: JSD between baseline and endline crop-share vectors on
  PRIMARY_CROP_SET + remainder 'other'.
- Exposures: irrigation share (USDA reported; SPAM _I zonal for others),
  perennial share (strict woody), HHI baseline.
- Emits analysis/design_matrix.csv, within_country_information.csv.
"""
import numpy as np
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "SUBNATIONAL_RIGIDITY_DESIGN_FREEZE"
M = pd.read_parquet(OUT / "analysis" / "admin_crop_observation_matrix.parquet")
XW = pd.read_csv(OUT / "04_CROP_CROSSWALK.csv",
                 usecols=["source", "source_crop", "canonical_crop", "lifecycle",
                          "in_primary_set"])
M = M.merge(XW, left_on=["source", "crop"], right_on=["source", "source_crop"],
            how="left")
M = M[M.canonical_crop.isin(list(set(XW.canonical_crop) -
                               {"aggregate", "noncrop", "unmapped"}))]

# pick vintages per (source,country): baseline year nearest 2002 within
# [1998,2008], endline nearest 2019 within [2013,2024], gap >= 8
def pick(years):
    years = np.array(sorted(set(years)))
    b = years[(years >= 1998) & (years <= 2008)]
    e = years[(years >= 2013) & (years <= 2024)]
    if not len(b) or not len(e):
        return None
    bb = b[np.argmin(np.abs(b - 2002))]
    ee = e[np.argmin(np.abs(e - 2019))]
    if ee - bb < 8:
        return None
    return bb, ee

PRIMARY = set(XW[xw_can := XW.in_primary_set.fillna(False)].canonical_crop)

def shares(sub, keep_primary=True):
    s = sub.groupby("canonical_crop").area_ha.sum()
    if keep_primary:
        prim = s[s.index.isin(PRIMARY)]
        other = s[~s.index.isin(PRIMARY)].sum()
        if other > 0:
            prim.loc["other_remainder"] = other
        s = prim
    t = s.sum()
    return (s / t) if t > 0 else s * np.nan

def jsd(p, q):
    p = p / p.sum(); q = q / q.sum(); m = 0.5 * (p + q)
    def k(a, b):
        return np.nansum(np.where(a > 0, a * np.log2(a / b), 0))
    return np.sqrt(0.5 * k(p, m) + 0.5 * k(q, m))

rows = []
for (src, ctry, uid, uname), g in M.groupby(["source", "country", "unit_id",
                                           "unit_name"]):
    years = g.year.unique()
    pv = pick(years)
    if pv is None:
        continue
    b, e = pv
    gb = g[g.year.between(b - 1, b + 1)]   # 3-yr smoothing around endpoints
    ge = g[g.year.between(e - 1, e + 1)]
    pb, pe = shares(gb), shares(ge)
    if pb.isna().all() or pe.isna().all() or len(pb) < 3 or len(pe) < 3:
        continue
    idx = pb.index.union(pe.index)
    pb = pb.reindex(idx, fill_value=0.0)
    pe = pe.reindex(idx, fill_value=0.0)
    if pb.sum() == 0 or pe.sum() == 0:
        continue
    life_b = gb.groupby("lifecycle").area_ha.sum()
    total_b = life_b.sum()
    perennial_strict = life_b.get("perennial_woody", 0.0) / total_b
    perennial_broad = (life_b.get("perennial_woody", 0.0) +
                       life_b.get("perennial_nonwoody", 0.0)) / total_b
    hhi = float((pb ** 2).sum())
    l1 = float(np.abs(pb - pe).sum())
    rows.append(dict(source=src, country=ctry, unit_id=uid, unit_name=uname,
                     y0=b, y1=e, gap=e - b,
                     jsd=jsd(pb.values, pe.values), l1=l1,
                     delta_hhi=float((pe ** 2).sum() - (pb ** 2).sum()),
                     hhi_baseline=hhi,
                     perennial_strict=perennial_strict,
                     perennial_broad=perennial_broad,
                     n_crops_b=len(pb), area_baseline=float(total_b)))

dm = pd.DataFrame(rows)
dm.to_csv(OUT / "analysis" / "design_matrix.csv", index=False)
print("units in design:", len(dm), "countries:", dm.country.nunique())
print(dm.jsd.describe())
print(dm.groupby("source").size())

wc = dm.groupby("country").agg(
    units=("unit_id", "nunique"),
    per_sd=("perennial_strict", "std"),
    hhi_sd=("hhi_baseline", "std"),
    jsd_mean=("jsd", "mean")).reset_index()
wc.to_csv(OUT / "analysis" / "within_country_information.csv", index=False)
print(wc.describe())
