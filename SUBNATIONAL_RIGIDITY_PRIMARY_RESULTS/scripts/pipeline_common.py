"""Shared helpers for the locked V4 subnational primary analysis."""
import hashlib
import numpy as np
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
V4 = ROOT / "SUBNATIONAL_RIGIDITY_LOCK_V4"
V3 = ROOT / "SUBNATIONAL_RIGIDITY_LOCK_V3"
RES = ROOT / "SUBNATIONAL_RIGIDITY_PRIMARY_RESULTS"
ANA = RES / "analysis"
FIG = RES / "figures"

SAMPLE = V4 / "analysis" / "PRIMARY_SUBNATIONAL_SAMPLE_LOCKED_V4.csv"
LOCK = V4 / "SUBNATIONAL_PRIMARY_ANALYSIS_LOCK_V4.yaml"
SEED = 20261003


def sha256(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def verify_lock():
    s = sha256(SAMPLE)
    l = sha256(LOCK)
    exp_s = (V4 / "analysis" / "PRIMARY_SUBNATIONAL_SAMPLE_LOCKED_V4.sha256")\
        .read_text().split()[0]
    exp_l = (V4 / "SUBNATIONAL_PRIMARY_ANALYSIS_LOCK_V4.sha256")\
        .read_text().split()[0]
    assert s == exp_s, "sample hash mismatch - ABORT"
    assert l == exp_l, "lock hash mismatch - ABORT"
    return s, l


def load_sample():
    dm = pd.read_csv(SAMPLE)
    blk = pd.read_csv(V4 / "analysis" / "admin_spatial_blocks_v4.csv")
    return dm.merge(blk[["unit_id", "lon", "lat",
                         "block_grid10", "block_grid15", "block_km"]],
                    on="unit_id")


def design(dm, irr_col="irr_share_base2000", extra=None):
    """OLS design on ORIGINAL scales: intercept + irr + mm + irr*mm +
    country FE (+ optional extra covariate columns)."""
    N = len(dm)
    cols = [np.ones(N), dm[irr_col].values, dm.mismatch_T.values,
            dm[irr_col].values * dm.mismatch_T.values]
    names = ["const", "irr", "mm", "irr_x_mm"]
    if extra:
        for c in extra:
            cols.append(dm[c].values.astype(float))
            names.append(c)
    fe = pd.get_dummies(dm.country, drop_first=True).values.astype(float)
    X = np.c_[np.column_stack(cols), fe]
    return X, names


def ols(X, y):
    b, res, rank, sv = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ b
    return b, resid


def block_boot_est(dm, X, y, block_col, B=999, seed=SEED):
    """Block bootstrap; returns array of coefficient rows (full b)."""
    rng = np.random.default_rng(seed)
    ub = dm[block_col].unique()
    pos = {u: np.where(dm[block_col].values == u)[0] for u in ub}
    out = []
    for _ in range(B):
        pick = rng.choice(len(ub), len(ub))
        rows_ = np.concatenate([pos[ub[i]] for i in pick])
        try:
            b, _ = ols(X[rows_], y[rows_])
            out.append(b)
        except Exception:
            pass
    return np.array(out)


def fit_all(dm, irr_col="irr_share_base2000", extra=None, frac=False):
    """Point fit. Returns (b, names). frac=True -> fractional logit GLM."""
    X, names = design(dm, irr_col, extra)
    y = dm.jsd.values
    if frac:
        import statsmodels.api as sm
        m = sm.GLM(np.clip(y, 1e-6, 1 - 1e-6), X,
                   family=sm.families.Binomial()).fit()
        return m.params, names
    b, _ = ols(X, y)
    return b, names
