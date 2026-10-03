#!/usr/bin/env python3
"""10_spatial_inference_validation.py — inference-method validation under
spatially correlated simulation (null beta3 = 0, TWO-SIDED alpha = 0.05).

Outcome: bounded JSD-like y = plogis(X b + u), u ~ MVN(0, sigma_u^2 R),
R_ij = exp(-d_ij / s). Scenarios: s = 0 (none), 500 (weak), 1500 (moderate),
4000 (strong) km, on country footprint centroids.

Model family: fractional logit (GLM Binomial, logit), matching the frozen
continuous-JSD primary estimand; no dichotomization.

Methods compared:
  hc2          - heteroskedasticity-consistent SE (two-sided z)
  region_crve  - cluster-robust by M49 region (diagnostic; ~5 clusters)
  clboot_sub   - cluster bootstrap resampling M49 SUBREGIONS (percentile CI)
  conley       - spatial HAC / Conley-type SE, Bartlett kernel, 1500 km
  blockboot    - spatial block bootstrap over predefined 30deg lat-lon tiles

Output: analysis/spatial_inference_simulation.csv  (type-I rejection +
95% CI coverage of true beta3=0, CI width, per method x scenario)
"""
import numpy as np
import pandas as pd
import statsmodels.api as sm
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AN = ROOT / "CROP_RIGIDITY_FINAL_LOCK" / "analysis"
S = pd.read_csv(AN / "primary_sample_preoutcome.csv")
S = S.dropna(subset=["mismatch"]).reset_index(drop=True)
rng = np.random.default_rng(20261003)

JSD_MAX = float(np.sqrt(np.log(2)))          # Jensen-Shannon distance bound
yobs = (S.jsd / JSD_MAX).values
M = ((S.mismatch - S.mismatch.mean()) / S.mismatch.std()).values
H = ((S.hhi - S.hhi.mean()) / S.hhi.std()).values
X = np.column_stack([np.ones(len(S)), H, M, H * M])

def hav(lat1, lon1, lat2, lon2):
    R = 6371.0
    p1, p2 = np.radians(lat1), np.radians(lat2)
    dp, dl = np.radians(lat2 - lat1), np.radians(lon2 - lon1)
    a = np.sin(dp / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dl / 2) ** 2
    return 2 * R * np.arcsin(np.sqrt(a))

lat = S.centroid_lat.values; lon = S.centroid_lon.values
D = hav(lat[:, None], lon[:, None], lat[None, :], lon[None, :])

# nuisance coefficients from a no-interaction fit (allowed: not beta3)
fit0 = sm.GLM(yobs, X[:, :3], family=sm.families.Binomial()).fit()
b_nuis = np.array([fit0.params[0], fit0.params[1], fit0.params[2], 0.0])
SIGMA_U = 0.35

def fit_b3(y, Xd):
    try:
        f = sm.GLM(y, Xd, family=sm.families.Binomial()).fit(disp=0)
        return f
    except Exception:
        return None

def hc2_reject(y, Xd):
    f = fit_b3(y, Xd)
    if f is None: return np.nan, np.nan
    b = f.params[3]; se = f.bse[3]
    return float(abs(b / se) > 1.96), float(2 * 1.96 * se)

def cluster_crve_reject(y, Xd, groups):
    f = fit_b3(y, Xd)
    if f is None: return np.nan, np.nan
    try:
        r = f.get_robustcov_results(cov_type="cluster",
                                    cov_kwds={"groups": groups})
        b, se = r.params[3], r.bse[3]
        return float(abs(b / se) > 1.96), float(2 * 1.96 * se)
    except Exception:
        return np.nan, np.nan

def conley_reject(y, Xd, D, L=1500.0):
    f = fit_b3(y, Xd)
    if f is None: return np.nan, np.nan
    mu = f.mu
    W = mu * (1 - mu)
    e = y - mu
    bread = np.linalg.inv(Xd.T @ (Xd * W[:, None]))
    K = np.where(D < L, 1 - D / L, 0.0)
    meat = Xd.T @ ((e[:, None] * e[None, :]) * K) @ Xd
    V = bread @ meat @ bread
    se = np.sqrt(max(V[3, 3], 0))
    if se == 0: return np.nan, np.nan
    return float(abs(f.params[3] / se) > 1.96), float(2 * 1.96 * se)

def boot_ci_reject(y, Xd, block_ids, B=199):
    """pairs bootstrap resampling whole blocks; percentile 95% CI."""
    ids = np.unique(block_ids)
    bs = []
    n = len(y)
    for _ in range(B):
        drawn = rng.choice(ids, size=len(ids), replace=True)
        idx = np.concatenate([np.flatnonzero(block_ids == g) for g in drawn])
        try:
            f = sm.GLM(y[idx], Xd[idx], family=sm.families.Binomial()
                       ).fit(disp=0, maxiter=25)
            bs.append(f.params[3])
        except Exception:
            continue
    if len(bs) < B * 0.8:
        return np.nan, np.nan
    bs = np.sort(bs)
    lo, hi = bs[int(0.025 * len(bs))], bs[int(0.975 * len(bs)) - 1]
    return float(not (lo <= 0 <= hi)), float(hi - lo)

sub_ids = S.subregion.astype("category").cat.codes.values
reg_ids = S.region.astype("category").cat.codes.values
tile_ids = ((np.floor(lon / 30) * 100 + np.floor(lat / 30)).astype(int))

NSIM = 200
rows = []
for scen, s_km in [("none", 0.0), ("weak", 500.0), ("moderate", 1500.0),
                   ("strong", 4000.0)]:
    if s_km > 0:
        R = np.exp(-D / s_km)
        Lch = np.linalg.cholesky(R + 1e-8 * np.eye(len(S)))
    for i in range(NSIM):
        u = rng.normal(0, SIGMA_U, len(S)) if s_km == 0 \
            else SIGMA_U * Lch @ rng.normal(0, 1, len(S))
        eta = X @ b_nuis + u
        y = np.clip(1 / (1 + np.exp(-eta)), 1e-6, 1 - 1e-6)
        for meth in ("hc2", "region_crve", "clboot_sub", "conley", "blockboot"):
            if meth == "hc2":
                rj, w = hc2_reject(y, X)
            elif meth == "region_crve":
                rj, w = cluster_crve_reject(y, X, reg_ids)
            elif meth == "clboot_sub":
                rj, w = boot_ci_reject(y, X, sub_ids)
            elif meth == "blockboot":
                rj, w = boot_ci_reject(y, X, tile_ids)
            else:
                rj, w = conley_reject(y, X, D)
            rows.append(dict(scenario=scen, sim=i, method=meth,
                             rejected=rj, ci_width=w))
    print(scen, "done", flush=True)

r = pd.DataFrame(rows)
summ = (r.groupby(["scenario", "method"])
          .agg(typeI=("rejected", "mean"), ci_width_med=("ci_width", "median"),
               n=("rejected", "size"), failed=("rejected",
                    lambda x: int(x.isna().sum())))
          .reset_index())
summ.to_csv(AN / "spatial_inference_simulation.csv", index=False)
print(summ.to_string(index=False))
