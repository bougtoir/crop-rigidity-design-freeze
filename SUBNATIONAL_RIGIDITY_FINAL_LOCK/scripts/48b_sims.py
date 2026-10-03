#!/usr/bin/env python3
"""Inference validation v2 + information simulation v2 (numpy fast path).
Requires analysis/admin_spatial_blocks.csv written by 48_spatial_blocks.py."""
import numpy as np
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FOUT = ROOT / "SUBNATIONAL_RIGIDITY_FINAL_LOCK"
blk = pd.read_csv(FOUT / "analysis" / "admin_spatial_blocks.csv")
dm = pd.read_csv(FOUT / "analysis" / "final_primary_design_matrix_preoutcome.csv")
dm = dm.merge(blk[["unit_id", "lon", "lat", "block_grid10", "block_km"]],
              on="unit_id", how="left")
dm = dm.dropna(subset=["lon", "irr_share_base2000", "mismatch_T",
                       "jsd"]).reset_index(drop=True)
N = len(dm)
cty = dm.country.values
ctys = sorted(dm.country.unique())
cty_ix = {c: np.where(cty == c)[0] for c in ctys}
CTY_DUM = np.zeros((N, len(ctys) - 1))
for j, c in enumerate(ctys[1:]):
    CTY_DUM[cty == c, j] = 1.0
X_FE = np.c_[np.ones(N), CTY_DUM]

irr = dm.irr_share_base2000.values
mm = dm.mismatch_T.values
def build(irr_, mm_):
    return np.c_[irr_, mm_, irr_ * mm_, X_FE]
XF = build(irr, mm)

latr = np.radians(dm.lat.values)
dlon = np.radians(dm.lon.values[:, None] - dm.lon.values[None, :])
dlat = latr[:, None] - latr[None, :]
hav = (np.sin(dlat / 2) ** 2 + np.cos(latr[:, None]) * np.cos(latr[None, :])
       * np.sin(dlon / 2) ** 2)
DIST = 6371.0 * 2 * np.arcsin(np.sqrt(np.clip(hav, 0, 1)))

blk_g = {b: np.where(dm.block_grid10.values == b)[0]
         for b in dm.block_grid10.unique()}
blk_k = {b: np.where(dm.block_km.values == b)[0]
         for b in dm.block_km.unique()}
cty_list = list(cty_ix.values())

def ols(X, y):
    b, *_ = np.linalg.lstsq(X, y, rcond=None)
    return b

def fit_y(y):
    return ols(XF, y)

def hc3_se(y, b):
    e = y - XF @ b
    XtXi = np.linalg.pinv(XF.T @ XF)
    h = np.sum((XF @ XtXi) * XF, axis=1)
    meat = XF * (e / np.clip(1 - h, 0.05, None))[:, None]
    return np.sqrt(np.diag(XtXi @ meat.T @ meat @ XtXi))[2]

def crve_se(y, b):
    e = y - XF @ b
    XtXi = np.linalg.pinv(XF.T @ XF)
    meat = np.zeros((XF.shape[1], XF.shape[1]))
    for ix in cty_list:
        sc = XF[ix].T @ e[ix]
        meat += np.outer(sc, sc)
    G = len(cty_list); K = XF.shape[1]
    corr_ = (G / (G - 1)) * ((N - 1) / (N - K))
    return np.sqrt(np.diag(corr_ * XtXi @ meat @ XtXi))[2]

def boot_se(y, blocks, B, rng):
    keys = list(blocks)
    est = []
    for _ in range(B):
        pick = rng.choice(len(keys), len(keys))
        rows_ = np.concatenate([blocks[keys[i]] for i in pick])
        try:
            est.append(ols(XF[rows_], y[rows_])[2])
        except Exception:
            pass
    return np.nanstd(est) if len(est) > 30 else np.nan

def pairs_se(y, B, rng):
    est = []
    for _ in range(B):
        pick = np.concatenate([ix[rng.choice(len(ix), len(ix))]
                               for ix in cty_list])
        try:
            est.append(ols(XF[pick], y[pick])[2])
        except Exception:
            pass
    return np.nanstd(est) if len(est) > 30 else np.nan

sd_y = np.nanstd(dm.jsd.values)
REPS, BB = 150, 50
rows = []
for rho_km, label in [(1.0, "independent"), (150.0, "weak"),
                      (500.0, "moderate"), (1500.0, "strong")]:
    C = np.exp(-DIST / rho_km) * sd_y ** 2
    np.fill_diagonal(C, np.diag(C) + 1e-8)
    L = np.linalg.cholesky(C)
    rng = np.random.default_rng(20261003 + int(rho_km))
    res = {m: [] for m in ("hc3", "crve", "pairs", "grid10", "km")}
    for rep in range(REPS):
        cre = rng.normal(0, sd_y * 0.3, size=len(ctys))
        cmap = np.array([ctys.index(c) for c in cty])
        y = cre[cmap] + L @ rng.normal(size=N)
        b = fit_y(y)
        res["hc3"].append((b[2], hc3_se(y, b)))
        res["crve"].append((b[2], crve_se(y, b)))
        res["pairs"].append((b[2], pairs_se(y, BB, rng)))
        res["grid10"].append((b[2], boot_se(y, blk_g, BB, rng)))
        res["km"].append((b[2], boot_se(y, blk_k, BB, rng)))
    for m, v in res.items():
        v = pd.DataFrame(v, columns=["b3", "se"]).dropna()
        rows.append(dict(scenario=label, rho_km=rho_km, method=m,
            n_sims=len(v), type_I=float((np.abs(v.b3) > 1.96 * v.se).mean()),
            coverage_null=float(((v.b3 - 1.96 * v.se <= 0)
                                 & (v.b3 + 1.96 * v.se >= 0)).mean()),
            median_ci_width=float((2 * 1.96 * v.se).median()),
            failure_rate=float(1 - len(v) / REPS)))
    print("done", label, flush=True)
si = pd.DataFrame(rows)
si.to_csv(FOUT / "analysis" / "spatial_inference_simulation_v2.csv",
          index=False)
print(si.round(3).to_string())

# ---------------- information simulation v2 ----------------
z_irr = (irr - irr.mean()) / irr.std()
z_mm = (mm - mm.mean()) / mm.std()
z_int = z_irr * z_mm
XZ = np.c_[z_irr, z_mm, z_int, X_FE]
rho0 = 500.0
C2 = np.exp(-DIST / rho0) * 0.5 ** 2
np.fill_diagonal(C2, np.diag(C2) + 1e-8)
L2 = np.linalg.cholesky(C2)
blk_gz = blk_g

def genz(rng, b3):
    lin = (0.10 * z_irr - 0.05 * z_mm + b3 * z_int
           + L2 @ rng.normal(size=N))
    return np.clip(dm.jsd.values + lin, 1e-4, 0.95)

def boot_se_z(y, B, rng):
    keys = list(blk_gz)
    est = []
    for _ in range(B):
        pick = rng.choice(len(keys), len(keys))
        rows_ = np.concatenate([blk_gz[keys[i]] for i in pick])
        try:
            est.append(ols(XZ[rows_], y[rows_])[2])
        except Exception:
            pass
    return np.nanstd(est) if len(est) > 30 else np.nan

info = []
for tb, lab in [(0.0, "null"), (0.25, "small"), (0.50, "moderate"),
                (0.75, "large")]:
    rng = np.random.default_rng(777 + int(tb * 100))
    est, se = [], []
    for rep in range(120):
        y = genz(rng, tb)
        est.append(ols(XZ, y)[2])
        se.append(boot_se_z(y, BB, rng))
    est = np.array(est); se = np.array(se); g = np.isfinite(se)
    info.append(dict(true_beta3=tb, label=lab, n_sims=int(g.sum()),
        bias=float(est[g].mean() - tb),
        rmse=float(np.sqrt(((est[g] - tb) ** 2).mean())),
        type_I=float((np.abs(est[g]) > 1.96 * se[g]).mean()) if tb == 0 else np.nan,
        coverage=float(((est[g] - 1.96 * se[g] <= tb)
                        & (est[g] + 1.96 * se[g] >= tb)).mean()),
        power=float((np.abs(est[g]) > 1.96 * se[g]).mean()) if tb else np.nan,
        median_ci_width=float(np.median(2 * 1.96 * se[g])),
        boot_fail_rate=float(1 - g.mean())))
    print("info done", lab, flush=True)
ir = pd.DataFrame(info)
ir.to_csv(FOUT / "analysis" / "information_simulation_v2.csv", index=False)
print(ir.round(3).to_string())
