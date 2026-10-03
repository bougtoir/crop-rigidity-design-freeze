#!/usr/bin/env python3
"""V4 information simulation — bounded DGP on the strict admin-1 sample.

Outcome-blind: uses ONLY the final-sample marginal JSD moments
(N=340, mean 0.293226, SD 0.173168, median 0.253861, min 0.0393,
max 0.9537 — analysis/jsd_marginal_summary_v4.csv). JSD here is the
distance sqrt(JSD divergence) on [0,1]: the implementation uses log2
(divergence bounded by 1 bit), so the theoretical max is 1.0.

DGP (bounded by construction):
  eta_i = alpha + g_country(i) + b1*z_irr + b2*z_mm + b3*z_int + s_i
  mu_i  = plogis(eta_i)
  Y_i   ~ Beta(mu_i * phi, (1 - mu_i) * phi)          (no clipping)

alpha and phi are calibrated (method of moments over 60 Monte Carlo
draws of eta) so that under b3=0 the marginal Y matches the V4 marginal
mean and SD. b1, b2 are assigned a priori (0.35, -0.20 on the link
scale); b3 is the assigned generating parameter. Under b3=0 the
generating-scale interaction is exactly 0 (<1e-16 by construction);
the induced JSD-scale OLS projection interaction is also computed and
reported (nonlinearity makes it ~1e-4, far below se ~0.02).

Effect grid: JSD-scale marginal contrasts {0, ±0.01, ±0.02, ±0.04}
= difference in the +1SD-mismatch effect between irrigation P75 and P25
groups; latent b3 solved by 1-D root find on the population contrast.

Frozen estimator tested: OLS + country FE + grid10 block bootstrap.

Reproducibility: byte-identical CSV per run (fixed seeds), verified by
package_validation_v4.py.
"""
import numpy as np
import pandas as pd
from pathlib import Path
from scipy.optimize import brentq

ROOT = Path(__file__).resolve().parents[1]
V4 = ROOT / "SUBNATIONAL_RIGIDITY_LOCK_V4"

dm = pd.read_csv(V4 / "analysis" / "PRIMARY_SUBNATIONAL_SAMPLE_LOCKED_V4.csv")
blk = pd.read_csv(V4 / "analysis" / "admin_spatial_blocks_v4.csv")
dm = dm.merge(blk[["unit_id", "lon", "lat", "block_grid10"]], on="unit_id")

z_irr = (dm.irr_share_base2000 - dm.irr_share_base2000.mean()) / dm.irr_share_base2000.std()
z_mm = (dm.mismatch_T - dm.mismatch_T.mean()) / dm.mismatch_T.std()
z_int0 = z_irr * z_mm
z_int = (z_int0 - z_int0.mean()) / z_int0.std()

N = len(dm)
X0 = np.c_[np.ones(N), pd.get_dummies(dm.country, drop_first=True).values.astype(float)]
X = np.c_[z_irr.values, z_mm.values, z_int.values, X0]

latr = np.radians(dm.lat.values)
dlon = np.radians(dm.lon.values[:, None] - dm.lon.values[None, :])
dlat = latr[:, None] - latr[None, :]
hav = (np.sin(dlat / 2) ** 2
       + np.cos(latr[:, None]) * np.cos(latr[None, :])
       * np.sin(dlon / 2) ** 2)
DIST = 6371.0 * 2 * np.arcsin(np.sqrt(np.clip(hav, 0, 1)))
RHO = 500.0
ETA_SD = 0.9
L = np.linalg.cholesky(np.exp(-DIST / RHO) * ETA_SD ** 2 + 1e-9 * np.eye(N))
cmap = {c: i for i, c in enumerate(sorted(dm.country.unique()))}
cidx = dm.country.map(cmap).values

MU_Y, SD_Y = 0.293226, 0.173168
B1, B2 = 0.35, -0.20


def plogis(x):
    return 1.0 / (1.0 + np.exp(-x))


def marginal_stats(alpha, phi, draws=60, seed=11):
    rng = np.random.default_rng(seed)
    ms, ss = [], []
    for _ in range(draws):
        eta = alpha + L @ rng.normal(size=N)
        mu = plogis(eta)
        y = rng.beta(mu * phi, (1 - mu) * phi)
        ms.append(y.mean())
        ss.append(y.std())
    return float(np.mean(ms)), float(np.mean(ss))


def calibrate():
    best = None
    for alpha in np.arange(-1.4, 0.4, 0.05):
        for phi in [4, 5, 6, 7, 8, 10, 12, 15, 20, 30]:
            m, s = marginal_stats(alpha, phi, draws=20)
            obj = abs(m - MU_Y) + abs(s - SD_Y)
            if best is None or obj < best[0]:
                best = (obj, alpha, phi)
    _, alpha, phi = best
    m, s = marginal_stats(alpha, phi, draws=60)
    return alpha, phi, m, s


ALPHA, PHI, CAL_M, CAL_S = calibrate()
print(f"calibrated alpha={ALPHA:.3f} phi={PHI} -> mean {CAL_M:.4f} "
      f"(target {MU_Y}), sd {CAL_S:.4f} (target {SD_Y})")


def contrast_for_b3(b3):
    """JSD-scale marginal contrast of the +1sd mismatch effect between
    irrigation-P75 and P25 groups, averaged over the sample's own units."""
    hi = z_irr.values >= z_irr.values[np.argsort(z_irr.values)[int(.75*N)]]
    lo = z_irr.values <= z_irr.values[np.argsort(z_irr.values)[int(.25*N)]]
    rng = np.random.default_rng(5)
    def delta(mask):
        # +1sd vs -1sd in z_mm, averaged over units in group
        up = plogis(ALPHA + B1*z_irr.values[mask] + B2*(z_mm.values[mask]+1)
                    + b3*z_int.values[mask])
        dn = plogis(ALPHA + B1*z_irr.values[mask] + B2*(z_mm.values[mask]-1)
                    - b3*z_int.values[mask])
        return float((up - dn).mean())
    return delta(hi) - delta(lo)


def solve_b3(target):
    if target == 0.0:
        return 0.0
    f = lambda b: contrast_for_b3(b) - target
    lo, hi = -3.0, 3.0
    if f(lo) * f(hi) > 0:
        return np.nan
    return brentq(f, lo, hi, xtol=1e-8)


def block_boot(y, rng, B=80):
    ub = dm.block_grid10.unique()
    pos = {u: np.where(dm.block_grid10.values == u)[0] for u in ub}
    est = []
    for _ in range(B):
        pick = rng.choice(len(ub), len(ub))
        rows_ = np.concatenate([pos[ub[i]] for i in pick])
        try:
            bb, *_ = np.linalg.lstsq(X[rows_], y[rows_], rcond=None)
            est.append(bb[2])
        except Exception:
            pass
    est = np.array(est)
    return (np.nanstd(est) if len(est) >= 30 else np.nan), len(est)


def gen(rng, b3):
    cre = rng.normal(0, ETA_SD * 0.3, size=len(cmap))
    eta = (ALPHA + cre[cidx] + B1 * z_irr.values + B2 * z_mm.values
           + b3 * z_int.values + L @ rng.normal(size=N))
    mu = plogis(eta)
    return rng.beta(mu * PHI, (1 - mu) * PHI), mu


rows = []
for target in [0.0, 0.01, 0.02, 0.04, -0.01, -0.02, -0.04]:
    b3_lat = solve_b3(target)
    rng = np.random.default_rng(20261003 + int(round(abs(target) * 1000))
                              + (0 if target >= 0 else 13))
    ests, ses, mus = [], [], []
    # induced population OLS coefficient of E[Y] on z_int (JSD-scale truth)
    ytmp, mutmp = gen(np.random.default_rng(9), b3_lat)
    bind, *_ = np.linalg.lstsq(X, mutmp, rcond=None)
    induced = float(bind[2])
    for rep in range(200):
        y, mu = gen(rng, b3_lat)
        b, *_ = np.linalg.lstsq(X, y, rcond=None)
        se, nb = block_boot(y, rng)
        ests.append(b[2])
        ses.append(se)
    e = np.array(ests)
    s = np.array(ses)
    good = np.isfinite(s)
    e, s = e[good], s[good]
    rows.append(dict(
        target_jsd_contrast=target, latent_b3=None if np.isnan(b3_lat) else float(b3_lat),
        induced_jsd_interaction=induced,
        n_sims=int(good.sum()),
        bias_vs_induced=float(e.mean() - induced),
        rmse_vs_induced=float(np.sqrt(((e - induced) ** 2).mean())),
        type_I=float((np.abs(e) > 1.96 * s).mean()) if target == 0 else np.nan,
        coverage=float(((e - 1.96 * s <= induced)
                        & (e + 1.96 * s >= induced)).mean()),
        power=float((np.abs(e) > 1.96 * s).mean()) if target != 0 else np.nan,
        median_ci_width=float(np.median(2 * 1.96 * s))))
res = pd.DataFrame(rows)
# exact-null check on generating scale: eta has no z_int term when b3=0
mu_null = plogis(ALPHA + B1*z_irr.values + B2*z_mm.values)
b0, *_ = np.linalg.lstsq(X, mu_null, rcond=None)
res["null_jsd_projection"] = float(b0[2])
res.to_csv(V4 / "analysis" / "information_simulation_v4.csv", index=False)
print(res.round(4).to_string(index=False))
print("latent null interaction: 0.0 (exact by construction)")
print("induced JSD-scale projection under b3=0:", float(b0[2]))
