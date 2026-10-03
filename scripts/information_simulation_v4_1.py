#!/usr/bin/env python3
"""V4.1 information simulation — PATCH of the effect-contrast mapping.

Identical bounded DGP to information_simulation_v4.py (fractional logit
+ Beta, V4 marginal JSD moments only, same spatial structure, same
grid10 block bootstrap, same country structure). The ONLY change is in
contrast_for_b3(): the +-1 SD mismatch counterfactual now RECOMPUTES the
interaction term at the shifted mismatch value instead of flipping the
sign of the observed interaction.

Frozen design standardization (same as the fitted design):
  z_int(mm) = (z_irr * mm - m0) / s0
where m0, s0 are the mean/SD of the observed z_irr*z_mm product. For
+1 SD mismatch: z_int_up = (z_irr*(z_mm+1) - m0)/s0; for -1 SD:
z_int_dn = (z_irr*(z_mm-1) - m0)/s0.

For every target JSD contrast {0, +-0.01, +-0.02, +-0.04} this reports:
target contrast, solved latent b3, achieved synthetic contrast, induced
OLS interaction, bias, RMSE, coverage, type-I/power, median CI width.

Outcome-blind: no unit-level observed JSD enters the DGP.
"""
import numpy as np
import pandas as pd
from pathlib import Path
from scipy.optimize import brentq

ROOT = Path(__file__).resolve().parents[1]
V4 = ROOT / "SUBNATIONAL_RIGIDITY_LOCK_V4"
OUT = ROOT / "SUBNATIONAL_RIGIDITY_PRIMARY_RESULTS"

dm = pd.read_csv(V4 / "analysis" / "PRIMARY_SUBNATIONAL_SAMPLE_LOCKED_V4.csv")
blk = pd.read_csv(V4 / "analysis" / "admin_spatial_blocks_v4.csv")
dm = dm.merge(blk[["unit_id", "lon", "lat", "block_grid10"]], on="unit_id")

z_irr = (dm.irr_share_base2000 - dm.irr_share_base2000.mean()) / dm.irr_share_base2000.std()
z_mm = (dm.mismatch_T - dm.mismatch_T.mean()) / dm.mismatch_T.std()
z_int0 = z_irr * z_mm
INT_M0, INT_S0 = float(z_int0.mean()), float(z_int0.std())
z_int = (z_int0 - INT_M0) / INT_S0

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


def z_int_shifted(z_mm_vals):
    """Interaction term at an arbitrary mismatch value, using the frozen
    observed-product standardization."""
    return (z_irr.values * z_mm_vals - INT_M0) / INT_S0


def contrast_for_b3(b3):
    """PATCHED: JSD-scale contrast of the +1sd-mismatch effect between
    irrigation-P75 and P25 units. The interaction term is recomputed at
    the shifted mismatch values (z_mm +/- 1), not sign-flipped."""
    hi = z_irr.values >= np.quantile(z_irr.values, 0.75)
    lo = z_irr.values <= np.quantile(z_irr.values, 0.25)
    zm = z_mm.values
    zi_up = z_int_shifted(zm + 1.0)
    zi_dn = z_int_shifted(zm - 1.0)
    def delta(mask):
        up = plogis(ALPHA + B1 * z_irr.values[mask]
                    + B2 * (zm[mask] + 1) + b3 * zi_up[mask])
        dn = plogis(ALPHA + B1 * z_irr.values[mask]
                    + B2 * (zm[mask] - 1) + b3 * zi_dn[mask])
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
    achieved = contrast_for_b3(b3_lat) if not np.isnan(b3_lat) else np.nan
    rng = np.random.default_rng(20261003 + int(round(abs(target) * 1000))
                              + (0 if target >= 0 else 13))
    ests, ses = [], []
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
        target_jsd_contrast=target,
        latent_b3=None if np.isnan(b3_lat) else float(b3_lat),
        achieved_synthetic_contrast=float(achieved),
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
mu_null = plogis(ALPHA + B1 * z_irr.values + B2 * z_mm.values)
b0, *_ = np.linalg.lstsq(X, mu_null, rcond=None)
res["null_jsd_projection"] = float(b0[2])
OUT.mkdir(exist_ok=True)
(OUT / "analysis").mkdir(exist_ok=True)
res.to_csv(OUT / "analysis" / "information_simulation_v4_1.csv", index=False)
print(res.round(4).to_string(index=False))
print("latent null interaction: 0.0 (exact by construction)")
print("induced JSD-scale projection under b3=0:", float(b0[2]))
