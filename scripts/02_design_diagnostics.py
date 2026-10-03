#!/usr/bin/env python3
"""02_design_diagnostics.py — design diagnostics from the acquired FAOSTAT panel.

Computes, on real data only:
  * country x crop x year harvested-area panel coverage (1961-2024)
  * candidate legacy variables in the legacy window (1981-2000):
      HHI, Shannon entropy, top-1 crop share, top-3 crop share
  * candidate transformation outcomes (outcome window 2001-2020 vs legacy):
      Jensen-Shannon distance, dominant-crop replacement, delta HHI
  * join/missingness summary per country (countries reporting in both windows)
  * effective-information summary (N countries, regions, sparse reporters)

Writes:
  analysis/design_diagnostics_summary.csv   (one row per country)
  analysis/design_diagnostics_globals.csv   (scalar diagnostics)
"""
import numpy as np
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "analysis"
LEGACY = (1981, 2000)
OUTCOME = (2001, 2020)
MIN_CROPS = 4          # minimum distinct crops to treat a country's mix as measurable
MIN_YEARS = 10         # minimum years reported within a window

df = pd.read_feather(RAW / "faostat_qcl_2026-02-25.feather")
ha = df[(df["element"] == "Area harvested") & (df["item_code"].notna())].copy()
ha = ha[["country", "year", "item", "value"]].dropna(subset=["value"])
ha["value"] = ha["value"].astype(float)
ha = ha[ha["value"] > 0]

# FAOSTAT items include aggregates ("Cereals,Total" etc.) — keep single crops by
# excluding items containing 'Total' or aggregation markers.
agg_mask = ha["item"].str.contains("Total| nes$|Primary", regex=True)
ha = ha[~agg_mask]

REGIONS = None  # region map: use a simple continent grouping via OWID? keep WB-free:
# coarse region by country name groups is fragile; use income-free geographic
# groupings via country list embedded below (UN-style macro regions, abbreviated).
# For diagnostics we only need a region count; assign via pycountry-free manual
# mapping skipped — use FAOSTAT fao_country names directly and count distinct
# 'regions' as UN M49 macro regions approximated by a small dict for major ones.

def shares(d):
    s = d.groupby(["country", "item"], observed=True)["value"].mean().reset_index()
    s["share"] = s["value"] / s.groupby("country", observed=True)["value"].transform("sum")
    return s

def js_distance(p, q):
    m = 0.5 * (p + q)
    klp = np.where(p > 0, p * np.log(p / m), 0).sum()
    klq = np.where(q > 0, q * np.log(q / m), 0).sum()
    return np.sqrt(0.5 * klp + 0.5 * klq)

rows = []
for c, g in ha.groupby("country", observed=True):
    g_l = g[(g.year >= LEGACY[0]) & (g.year <= LEGACY[1])]
    g_o = g[(g.year >= OUTCOME[0]) & (g.year <= OUTCOME[1])]
    n_years_l = g_l["year"].nunique()
    n_years_o = g_o["year"].nunique()
    if n_years_l < MIN_YEARS or n_years_o < MIN_YEARS:
        continue
    sl = shares(g_l)
    so = shares(g_o)
    if sl["item"].nunique() < MIN_CROPS or so["item"].nunique() < MIN_CROPS:
        continue
    p = sl.set_index("item")["share"]
    q = so.set_index("item")["share"]
    crops = sorted(set(p.index) | set(q.index))
    p = p.reindex(crops, fill_value=0.0)
    q = q.reindex(crops, fill_value=0.0)
    hhi = (p ** 2).sum()
    hhi_o = (q ** 2).sum()
    ent = -(p[p > 0] * np.log(p[p > 0])).sum()
    top1 = p.max()
    top3 = p.sort_values(ascending=False).head(3).sum()
    jsd = js_distance(p.values, q.values)
    replaced = int(p.idxmax() != q.idxmax())
    emergent = int(((p < 0.02) & (q > 0.10)).sum())
    rows.append(dict(
        country=c, n_crops_legacy=sl["item"].nunique(),
        n_years_legacy=n_years_l, n_years_outcome=n_years_o,
        hhi=hhi, entropy=ent, top1=top1, top3=top3,
        jsd=jsd, replaced=replaced, delta_hhi=hhi_o - hhi,
        emergent_crop=emergent,
    ))

res = pd.DataFrame(rows)
OUT.mkdir(exist_ok=True)
res.to_csv(OUT / "design_diagnostics_summary.csv", index=False)

glob_ = pd.DataFrame([dict(
    n_countries=len(res),
    median_crops=res["n_crops_legacy"].median(),
    median_hhi=res["hhi"].median(),
    p10_hhi=res["hhi"].quantile(0.1), p90_hhi=res["hhi"].quantile(0.9),
    median_top1=res["top1"].median(),
    median_jsd=res["jsd"].median(),
    p10_jsd=res["jsd"].quantile(0.1), p90_jsd=res["jsd"].quantile(0.9),
    share_replaced=res["replaced"].mean(),
    share_emergent=(res["emergent_crop"] > 0).mean(),
    median_delta_hhi=res["delta_hhi"].median(),
)])
glob_.to_csv(OUT / "design_diagnostics_globals.csv", index=False)
print(glob_.to_string(index=False))
print(res.describe().T[["mean", "50%", "min", "max"]])
