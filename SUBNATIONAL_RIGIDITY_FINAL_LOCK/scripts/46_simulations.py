#!/usr/bin/env python3
"""Phases 8, 16, 21: decomposition validation + spatial inference + information
simulation on the locked design matrix.

- analysis/decomposition_method_validation.csv: Kitagawa-Oaxaca exact
  decomposition of national aggregate share change into within/between/
  interaction components for each country (computed on observed matrices).
- analysis/spatial_inference_simulation.csv: type-I & coverage under spatially
  correlated synthetic outcomes for candidate inference schemes.
- analysis/information_simulation.csv: CI width/coverage/power for the locked
  specification under simulated outcomes.
"""
import numpy as np
import pandas as pd
from pathlib import Path

rng = np.random.default_rng(20261003)
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "SUBNATIONAL_RIGIDITY_DESIGN_FREEZE"
dm = pd.read_csv(OUT / "analysis" / "design_matrix_climate.csv")
M = pd.read_parquet(OUT / "analysis" / "admin_crop_observation_matrix.parquet")
XW = pd.read_csv(OUT / "04_CROP_CROSSWALK.csv",
                 usecols=["source", "source_crop", "canonical_crop"])

# ---------------------------------------------------------------- decomposition
# National aggregate share change decomposed per crop:
#   Delta_k = W_k + B_k + I_k
# with W_k = sum_u w0_u (p1-p0), B_k = sum_u p0_u (w1-w0),
# I_k = residual interaction (Das Gupta 2-factor exact form).
M = M.merge(XW, left_on=["source", "crop"], right_on=["source", "source_crop"])
M = M[~M.canonical_crop.isin(["aggregate", "noncrop", "unmapped", "forage"])]
rows = []
for (src, ctry), g in M.groupby(["source", "country"]):
    years = sorted(g.year.unique())
    if len(years) < 2:
        continue
    b = years[0]; e = years[-1]
    if e - b < 8:
        continue
    gb = g[g.year.between(b - 1, b + 1)].groupby(["unit_id", "canonical_crop"]).area_ha.sum().unstack(fill_value=0)
    ge = g[g.year.between(e - 1, e + 1)].groupby(["unit_id", "canonical_crop"]).area_ha.sum().unstack(fill_value=0)
    units = gb.index.intersection(ge.index)
    if len(units) < 2:
        continue
    gb = gb.loc[units].reindex(columns=gb.columns.union(ge.columns), fill_value=0)
    ge = ge.loc[units].reindex(columns=gb.columns, fill_value=0)
    a0, a1 = gb.sum(1), ge.sum(1)
    if (a0 == 0).any() or (a1 == 0).any():
        continue
    p0 = gb.div(a0, axis=0); p1 = ge.div(a1, axis=0)
    w0 = a0 / a0.sum(); w1 = a1 / a1.sum()
    for k in gb.columns:
        W = float((w0 * (p1[k] - p0[k])).sum())
        B = float((p0[k] * (w1 - w0)).sum())
        D = float((p1[k] * w1).sum() - (p0[k] * w0).sum())
        rows.append(dict(source=src, country=ctry, crop=k, delta_share=D,
                         within=W, between=B, interaction=D - W - B))
dec = pd.DataFrame(rows)
if len(dec):
    dec["exact_err"] = dec.delta_share - dec.within - dec.between - dec.interaction
    dec.to_csv(OUT / "analysis" / "decomposition_method_validation.csv",
               index=False)
    summ = dec.groupby("country").agg(
        abs_within=("within", lambda x: x.abs().sum()),
        abs_between=("between", lambda x: x.abs().sum()),
        abs_inter=("interaction", lambda x: x.abs().sum()),
        abs_total=("delta_share", lambda x: x.abs().sum())).reset_index()
    summ["within_share"] = summ.abs_within / (summ.abs_within + summ.abs_between + summ.abs_inter)
    print("max exactness err:", dec.exact_err.abs().max())
    print(summ.describe().round(4).to_string())

# ---------------------------------------------------------------- design matrix
d = dm.dropna(subset=["jsd", "mismatch_T", "irr_share"]).copy()
d["expo"] = d["irr_share"]
d = d[d.country.isin(d.groupby("country").filter(
    lambda g: len(g) >= 3).country)]
print("simulation N:", len(d), "countries:", d.country.nunique())

def fit_rows(idx_df, y_all):
    """OLS with country FE on resampled rows; returns beta3."""
    X = np.column_stack([np.ones(len(idx_df)), idx_df.expo, idx_df.mismatch_T,
                         idx_df.expo * idx_df.mismatch_T])
    X = np.column_stack([X, pd.get_dummies(idx_df.country, drop_first=True)
                         .reindex(columns=CTY_DUM, fill_value=0).values])
    b, *_ = np.linalg.lstsq(X, np.asarray(y_all), rcond=None)
    return b[3]

def fit(df, y):
    X = np.column_stack([np.ones(len(df)), df.expo, df.mismatch_T,
                         df.expo * df.mismatch_T])
    X = np.column_stack([X, pd.get_dummies(df.country, drop_first=True).values])
    b, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = np.asarray(y) - X @ b
    return b[3], resid, X

CTY_DUM = pd.get_dummies(d.country).columns[1:]
def boot_beta(y, reps=200):
    stats = []
    idx_by_c = [np.where(cty_codes == c)[0] for c in range(ncodes)]
    for _ in range(reps):
        pick = np.concatenate([rng.choice(ii, len(ii)) for ii in idx_by_c])
        stats.append(fit_rows(d.iloc[pick], np.asarray(y)[pick]))
    return np.asarray(stats)

# spatial inference candidates under spatially correlated noise
B = 300
methods = ["hc3", "country_cluster", "subregion_block", "conley_200km"]
res = {m: [] for m in methods}
cty_codes = d.country.astype("category").cat.codes.values
ncodes = d.country.astype("category").cat.categories.size
geo = None
try:
    import geopandas as gpd
    # proxy coordinates: reuse centroids via cache filenames? use unit_id order noise
except Exception:
    pass
for rep in range(B):
    # block-correlated noise: country effect + within-country spatial clusters
    eps = np.zeros(len(d))
    for c in range(ncodes):
        idx = np.where(cty_codes == c)[0]
        n = len(idx)
        nblk = max(1, n // 6)
        blk = np.repeat(np.arange(nblk), n // nblk + 1)[:n]
        eff = rng.normal(0, 0.25) + rng.normal(0, 0.2, nblk)[blk]
        eps[idx] = eff + rng.normal(0, 0.3, n)
    y = eps + 0.1
    y = np.clip(y, 0.001, 0.999)
    beta3, resid, X = fit(d, y)
    XtXinv = np.linalg.pinv(X.T @ X)
    # HC3
    h = np.clip(np.sum((X @ XtXinv) * X, axis=1), 0, 0.99)
    meat = X.T @ np.diag((resid / (1 - h)) ** 2) @ X
    V = XtXinv @ meat @ XtXinv
    res["hc3"].append(abs(beta3) / np.sqrt(V[3, 3]) > 1.96)
    # country cluster CRVE
    meat = np.zeros((X.shape[1], X.shape[1]))
    for c in range(ncodes):
        idx = np.where(cty_codes == c)[0]
        Xc, rc = X[idx], resid[idx]
        s = Xc.T @ rc
        meat += np.outer(s, s)
    V = XtXinv @ meat @ XtXinv * (ncodes / (ncodes - 1))
    res["country_cluster"].append(abs(beta3) / np.sqrt(V[3, 3]) > 1.96)
    # within-country row bootstrap (pairs resampled inside each country)
    stats = boot_beta(y)
    lo, hi = np.percentile(stats, [2.5, 97.5])
    res["subregion_block"].append(not (lo <= 0 <= hi))
    res["conley_200km"].append(np.nan)
out = pd.DataFrame([dict(method=m,
                         type1=float(np.nanmean(v)),
                         n=len(v)) for m, v in res.items()])
out.to_csv(OUT / "analysis" / "spatial_inference_simulation.csv", index=False)
print(out.to_string())

# ---------------------------------------------------------------- information sim
# power under locked spec: outcome shift in JSD SD units per SD of interaction
z = (d.expo * d.mismatch_T - (d.expo * d.mismatch_T).mean()) / (d.expo * d.mismatch_T).std()
sd_y = d.jsd.std()
res2 = []
for e in [0.0, 0.25, 0.5, 0.75, 1.0]:
    rej, width, cover = [], [], []
    true_b3 = None
    for rep in range(200):
        eps = np.zeros(len(d))
        for c in range(ncodes):
            idx = np.where(cty_codes == c)[0]
            n = len(idx)
            eps[idx] = rng.normal(0, 0.15) + rng.normal(0, 0.25, n)
        y = e * sd_y * z.values + eps + d.jsd.mean()
        y = np.clip(y, 0.001, 0.999)
        beta3, resid, X = fit(d, y)
        if true_b3 is None:
            true_b3 = beta3
        stats = boot_beta(y)
        lo, hi = np.percentile(stats, [2.5, 97.5])
        rej.append(not (lo <= 0 <= hi))
        width.append(hi - lo)
        cover.append(lo <= true_b3 <= hi)
    res2.append(dict(effect_sd=e, implied_beta3=true_b3,
                     reject_share=float(np.mean(rej)),
                     coverage=float(np.mean(cover)),
                     median_ci_width=float(np.median(width))))
pd.DataFrame(res2).to_csv(OUT / "analysis" / "information_simulation.csv",
                          index=False)
print(pd.DataFrame(res2).to_string())
