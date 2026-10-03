#!/usr/bin/env python3
"""V3 information simulation — fully outcome-blind and exactly reproducible.

DGP (issue 3 compliance):
  * NO observed unit-level JSD is used anywhere. Baseline outcome values
    are drawn from a parametric model parameterized ONLY by marginal
    moments (overall mean/SD of the JSD support) — mean 0.13, SD 0.09 —
    plus a fresh country random effect per replicate.
  * Predictors z_irr, z_mm, z_int are the standardized observed exposures
    (exposures are not the outcome; they define the estimand design).
  * Linear DGP: Y = mu + g_country + 0.10 z_irr - 0.05 z_mm + b3 z_int
    + spatially correlated noise. Because E[Y|X] = X beta exactly, the
    population OLS coefficient on z_int equals b3 to machine precision;
    under b3 = 0 the induced interaction is 0 < 1e-8 by construction.
  * Estimator frozen: OLS + country FE, 10deg grid block bootstrap SE.

Reports per scenario: true generating b3, induced marginal contrast,
bias, RMSE, coverage, type-I, CI width, power.

Reproducibility: running this script twice produces byte-identical
analysis/information_simulation_v3.csv (verified by package_validation).
"""
import numpy as np
import pandas as pd
import geopandas as gpd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "SUBNATIONAL_RIGIDITY_DESIGN_FREEZE"
V3 = ROOT / "SUBNATIONAL_RIGIDITY_LOCK_V3"
RAW = ROOT / "data" / "raw"

dm = pd.read_csv(V3 / "analysis" / "PRIMARY_SUBNATIONAL_SAMPLE_LOCKED.csv")
blk = pd.read_csv(V3 / "analysis" / "admin_spatial_blocks_v3.csv")
dm = dm.merge(blk[["unit_id", "lon", "lat", "block_grid10"]], on="unit_id")

# ---- standardized predictors (exposures only, never the outcome) ----
z_irr = (dm.irr_share_base2000 - dm.irr_share_base2000.mean()) / dm.irr_share_base2000.std()
z_mm = (dm.mismatch_T - dm.mismatch_T.mean()) / dm.mismatch_T.std()
z_int = (z_irr * z_mm)
z_int = (z_int - z_int.mean()) / z_int.std()   # re-standardized product

N = len(dm)
X0 = np.c_[np.ones(N), pd.get_dummies(dm.country, drop_first=True).values.astype(float)]
X = np.c_[z_irr.values, z_mm.values, z_int.values, X0]
XtXi = np.linalg.pinv(X.T @ X)

# ---- spatial noise ----
latr = np.radians(dm.lat.values)
dlon = np.radians(dm.lon.values[:, None] - dm.lon.values[None, :])
dlat = latr[:, None] - latr[None, :]
hav = (np.sin(dlat / 2) ** 2
       + np.cos(latr[:, None]) * np.cos(latr[None, :])
       * np.sin(dlon / 2) ** 2)
DIST = 6371.0 * 2 * np.arcsin(np.sqrt(np.clip(hav, 0, 1)))
RHO = 500.0
SD_Y = 0.09          # marginal-moment noise scale (JSD-scale SD), not per-unit data
MU = 0.13            # marginal-moment baseline mean on JSD support
L = np.linalg.cholesky(np.exp(-DIST / RHO) * SD_Y ** 2 + 1e-9 * np.eye(N))
cmap = {c: i for i, c in enumerate(sorted(dm.country.unique()))}
cidx = dm.country.map(cmap).values

B_IRR, B_MM = 0.10, -0.05          # standardized main effects (assigned)


def gen(rng, b3):
    cre = rng.normal(0, SD_Y * 0.3, size=len(cmap))
    return (MU + cre[cidx] + B_IRR * z_irr.values + B_MM * z_mm.values
            + b3 * z_int.values + L @ rng.normal(size=N))


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


# ---- induced marginal contrast (JSD units): mean over +/-1sd cells ----
def induced_contrast(b3):
    hi_irr = z_irr.values >= np.median(z_irr.values)
    hi_mm = z_mm.values >= np.median(z_mm.values)
    # expected change in mean Y per unit b3 (z_int is standardized)
    return float(b3 * (z_int.values[hi_irr & hi_mm].mean()
                       - z_int.values[~hi_irr & ~hi_mm].mean()))


rows = []
SEED0 = 20261003
for b3, lab in [(0.0, "null"), (0.15, "small"), (0.30, "moderate"),
                (0.50, "large"), (-0.15, "small_neg"), (-0.30, "moderate_neg"),
                (-0.50, "large_neg")]:
    rng = np.random.default_rng(SEED0 + int(round(abs(b3) * 1000)) + (0 if b3 >= 0 else 7))
    ests, ses, nfail = [], [], 0
    for rep in range(200):
        y = gen(rng, b3)
        b, *_ = np.linalg.lstsq(X, y, rcond=None)
        se, nb = block_boot(y, rng)
        ests.append(b[2])
        ses.append(se)
        nfail += int(nb < 80)
    ests = np.array(ests)
    ses = np.array(ses)
    good = np.isfinite(ses)
    e, s = ests[good], ses[good]
    rows.append(dict(
        true_b3=b3, label=lab, n_sims=int(good.sum()),
        induced_marginal_contrast=induced_contrast(b3),
        bias=float(e.mean() - b3),
        rmse=float(np.sqrt(((e - b3) ** 2).mean())),
        type_I=float((np.abs(e) > 1.96 * s).mean()) if b3 == 0 else np.nan,
        coverage=float(((e - 1.96 * s <= b3)
                        & (e + 1.96 * s >= b3)).mean()),
        power=float((np.abs(e) > 1.96 * s).mean()) if b3 != 0 else np.nan,
        median_ci_width=float(np.median(2 * 1.96 * s)),
        boot_fail_rate=float(nfail / 200)))

res = pd.DataFrame(rows)
# exact-null check: population OLS coef on z_int under b3=0 == 0 exactly
mu0 = MU + B_IRR * z_irr.values + B_MM * z_mm.values + 0.0 * z_int.values
b0, *_ = np.linalg.lstsq(X, mu0, rcond=None)
res["null_exactness_check"] = float(abs(b0[2]))
assert abs(b0[2]) < 1e-8, "induced null interaction not < 1e-8"
res.to_csv(V3 / "analysis" / "information_simulation_v3.csv", index=False)
print(res.round(4).to_string(index=False))
print("exact null interaction:", abs(b0[2]))
