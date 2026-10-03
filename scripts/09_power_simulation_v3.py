#!/usr/bin/env python3
"""09_power_simulation_v3.py — power/precision for the FROZEN primary analysis.

Differences from v2 (all fixes from the final audit):
  * dominant-crop mismatch on exactly the primary sample (N=147), not the
    146-country portfolio file;
  * continuous bounded JSD outcome under the frozen family (fractional
    logit), no dichotomization;
  * TWO-SIDED inference, alpha = 0.05, 95% CIs; precision (CI width)
    reported alongside power;
  * symmetric beta3 grid (0, +-0.3, +-0.6, +-1.0 on standardized scale);
  * spatially correlated latent noise at the 'moderate' scenario scale
    (exp(-d/1500 km), sigma_u=0.35) to match the validated DGP;
  * inference method = FROZEN_METHOD (set below after spatial validation).

Output: analysis/power_simulation_v3.csv
"""
import sys
import numpy as np
import pandas as pd
import statsmodels.api as sm
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AN = ROOT / "CROP_RIGIDITY_FINAL_LOCK" / "analysis"
FROZEN_METHOD = sys.argv[1] if len(sys.argv) > 1 else "conley"

S = pd.read_csv(AN / "primary_sample_preoutcome.csv")
S = S.dropna(subset=["mismatch"]).reset_index(drop=True)
rng = np.random.default_rng(20261003)
JSD_MAX = float(np.sqrt(np.log(2)))
yobs = (S.jsd / JSD_MAX).values
M = ((S.mismatch - S.mismatch.mean()) / S.mismatch.std()).values
H = ((S.hhi - S.hhi.mean()) / S.hhi.std()).values
X = np.column_stack([np.ones(len(S)), H, M, H * M])
fit0 = sm.GLM(yobs, X[:, :3], family=sm.families.Binomial()).fit()

def hav(lat1, lon1, lat2, lon2):
    R = 6371.0
    p1, p2 = np.radians(lat1), np.radians(lat2)
    dp, dl = np.radians(lat2 - lat1), np.radians(lon2 - lon1)
    a = np.sin(dp / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dl / 2) ** 2
    return 2 * R * np.arcsin(np.sqrt(a))

lat = S.centroid_lat.values; lon = S.centroid_lon.values
D = hav(lat[:, None], lon[:, None], lat[None, :], lon[None, :])
S_KM, SIGMA_U = 1500.0, 0.35
R = np.exp(-D / S_KM)
Lch = np.linalg.cholesky(R + 1e-8 * np.eye(len(S)))
sub_ids = S.subregion.astype("category").cat.codes.values
tile_ids = ((np.floor(lon / 30) * 100 + np.floor(lat / 30)).astype(int))

def boot_ci(y, Xd, block_ids, B=199):
    ids = np.unique(block_ids); bs = []
    for _ in range(B):
        drawn = rng.choice(ids, size=len(ids), replace=True)
        idx = np.concatenate([np.flatnonzero(block_ids == g) for g in drawn])
        try:
            f = sm.GLM(y[idx], Xd[idx], family=sm.families.Binomial()
                       ).fit(disp=0, maxiter=25)
            bs.append(f.params[3])
        except Exception:
            continue
    if len(bs) < B * 0.8: return (np.nan, np.nan)
    bs = np.sort(bs)
    return bs[int(0.025 * len(bs))], bs[int(0.975 * len(bs)) - 1]

def decide(y, Xd, method):
    f = sm.GLM(y, Xd, family=sm.families.Binomial()).fit(disp=0)
    b3 = f.params[3]
    if method == "conley":
        mu = f.mu; W = mu * (1 - mu); e = y - mu
        bread = np.linalg.inv(Xd.T @ (Xd * W[:, None]))
        K = np.where(D < 1500.0, 1 - D / 1500.0, 0.0)
        meat = Xd.T @ ((e[:, None] * e[None, :]) * K) @ Xd
        V = bread @ meat @ bread
        se = np.sqrt(max(V[3, 3], 0))
        return b3, se, float(abs(b3 / se) > 1.96), 2 * 1.96 * se
    if method == "hc2":
        se = f.bse[3]
        return b3, se, float(abs(b3 / se) > 1.96), 2 * 1.96 * se
    bid = sub_ids if method == "clboot_sub" else tile_ids
    lo, hi = boot_ci(y, Xd, bid)
    if np.isnan(lo): return b3, np.nan, np.nan, np.nan
    return b3, (hi - lo) / 3.92, float(not (lo <= 0 <= hi)), hi - lo

NSIM = 200
rows = []
for b3_true in [-1.0, -0.6, -0.3, 0.0, 0.3, 0.6, 1.0]:
    b = np.array([fit0.params[0], fit0.params[1], fit0.params[2], b3_true])
    rej, wid, cov = [], [], []
    for i in range(NSIM):
        u = SIGMA_U * Lch @ rng.normal(0, 1, len(S))
        y = np.clip(1 / (1 + np.exp(-(X @ b + u))), 1e-6, 1 - 1e-6)
        b3h, se, rj, w = decide(y, X, FROZEN_METHOD)
        rej.append(rj); wid.append(w)
        cov.append(float((b3h - 1.96 * se) <= b3_true <= (b3h + 1.96 * se))
                   if np.isfinite(se) else np.nan)
    rows.append(dict(method=FROZEN_METHOD, beta3=b3_true, n=len(S),
                     reject_rate=float(np.nanmean(rej)),
                     coverage=float(np.nanmean(cov)),
                     median_ci_width=float(np.nanmedian(wid)),
                     n_sims=NSIM))
    print(b3_true, rows[-1]["reject_rate"], flush=True)

pd.DataFrame(rows).to_csv(AN / "power_simulation_v3.csv", index=False)
print("wrote power_simulation_v3.csv")
