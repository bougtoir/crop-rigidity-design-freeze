#!/usr/bin/env python3
"""Final-lock repair, issues 2-3: real spatial blocks, inference validation
under geographically correlated residuals, and repaired information
simulation with analytically known true coefficients."""
import json
import numpy as np
import pandas as pd
import geopandas as gpd
import rasterio
from rasterio.features import rasterize
from pathlib import Path
from scipy.cluster.vq import kmeans2

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "SUBNATIONAL_RIGIDITY_DESIGN_FREEZE"
FOUT = ROOT / "SUBNATIONAL_RIGIDITY_FINAL_LOCK"
RAW = ROOT / "data" / "raw"
dm = pd.read_csv(FOUT / "analysis" / "final_primary_design_matrix_preoutcome.csv")
xw = pd.read_csv(OUT / "ADMIN_BOUNDARY_CROSSWALK.csv")

# ---------- centroids (recompute quickly) ----------
gadm = gpd.read_file(RAW / "gadm410" / "gadm_410-levels.gpkg", layer="ADM_1",
                     columns=["GID_1"])
gid2geom = dict(zip(gadm["GID_1"], gadm.geometry))
nuts = {}
for lvl in (1, 2):
    g = gpd.read_file(RAW / "subnat" / f"nuts2021_l{lvl}.geojson")
    nuts.update(dict(zip(g["NUTS_ID"], g.geometry)))
hv = gpd.read_file(RAW / "subnat" / "hvstat_africa_boundary_v1.2.gpkg")
hv["_key"] = ("HV1:" + hv["country_code"].astype(str) + ":"
              + hv["admin_1"].fillna("").astype(str))
hv_units = {}
for k, s in hv[hv["admin_1"].notna()].groupby("_key"):
    hv_units[k] = s.union_all()
for _, r in hv[hv["admin_1"].isna()].iterrows():
    hv_units["HV2:" + r["fnid"]] = r.geometry
gid_of = xw.drop_duplicates("unit_id").set_index("unit_id")["gadm41_gid"]
lon = {}; lat = {}
for uid in dm.unit_id.unique():
    g = None
    gid = gid_of.get(uid)
    if pd.notna(gid) and gid in gid2geom:
        g = gid2geom[gid]
    elif uid in hv_units:
        g = hv_units[uid]
    elif uid in nuts:
        g = nuts[uid]
    if g is not None:
        c = g.centroid
        lon[uid], lat[uid] = c.x, c.y
dm["lon"] = dm.unit_id.map(lon); dm["lat"] = dm.unit_id.map(lat)
# analysis sample: complete primary variables (baseline irrigation, mismatch,
# JSD) — locked missingness rule; units without a pre-outcome exposure
# cannot enter the model.
dm = dm.dropna(subset=["lon", "irr_share_base2000", "mismatch_T",
                       "jsd"]).reset_index(drop=True)
N = len(dm); print("units with geometry:", N)

# ---------- block schemes ----------
def grid_block(lon_, lat_, size):
    return (np.floor(lon_ / size).astype(int).astype(str) + ":"
            + np.floor(lat_ / size).astype(int).astype(str))

dm["block_grid10"] = grid_block(dm.lon, dm.lat, 10.0)
# within-country centroid clustering: split each country into up to
# ceil(nunits/6) geographic clusters via kmeans
rng0 = np.random.default_rng(0)
dm["block_km"] = ""
for c, idx in dm.groupby("country").groups.items():
    sub = dm.loc[idx]
    k = max(1, int(np.ceil(len(sub) / 6)))
    if k <= 1 or len(sub) < 4:
        dm.loc[idx, "block_km"] = c + ":0"
        continue
    xy = np.c_[sub.lon, sub.lat]
    try:
        cen, lab = kmeans2(xy, k, seed=rng0, minit="++")
    except Exception:
        lab = np.arange(len(sub)) % k
    dm.loc[idx, "block_km"] = [c + ":" + str(int(v)) for v in lab]

rows = []
for col in ("block_grid10", "block_km"):
    g = dm.groupby(col)
    sz = g.size()
    diam = g.apply(lambda s: float(np.sqrt((s.lon.max()-s.lon.min())**2 +
        (s.lat.max()-s.lat.min())**2)), include_groups=False)
    rows.append(dict(scheme=col, n_blocks=int(sz.size),
                     units_per_block_med=float(sz.median()),
                     units_per_block_max=int(sz.max()),
                     singleton_blocks=int((sz == 1).sum()),
                     countries_crossed=int((g["country"].nunique() > 1).sum()),
                     median_diameter_deg=float(diam.median())))
blk_desc = pd.DataFrame(rows)
dm[["unit_id", "country", "lon", "lat", "block_grid10",
    "block_km"]].to_csv(FOUT / "analysis" / "admin_spatial_blocks.csv",
                        index=False)
blk_desc.to_csv(FOUT / "analysis" / "admin_spatial_blocks_describe.csv",
                index=False)
print(blk_desc.to_string())

# ---------- estimation machinery ----------
X0 = np.c_[np.ones(N), pd.get_dummies(dm.country, drop_first=True).values.astype(float)]
def fit_rows(d, y):
    X = np.c_[d.irr_share_base2000.values, d.mismatch_T.values,
              (d.irr_share_base2000 * d.mismatch_T).values, X0[d.index.values]]
    b, *_ = np.linalg.lstsq(X, y, rcond=None)
    return b

def hc3(X, y, b):
    e = y - X @ b
    XtXi = np.linalg.pinv(X.T @ X)
    h = np.sum((X @ XtXi) * X, axis=1)
    meat = X * (e / np.clip(1 - h, 0.05, None))[:, None]
    cov = XtXi @ meat.T @ meat @ XtXi
    return np.sqrt(np.diag(cov))

def country_crve(X, y, b, grp):
    e = y - X @ np.linalg.lstsq(X, y, rcond=None)[0]
    XtXi = np.linalg.pinv(X.T @ X)
    meat = np.zeros((X.shape[1], X.shape[1]))
    for _, ix in pd.Series(grp).groupby(grp).groups.items():
        ix = list(ix)
        sc = X[ix].T @ e[ix]
        meat += np.outer(sc, sc)
    G = len(np.unique(grp))
    K = X.shape[1]
    corr_ = (G / (G - 1)) * ((N - 1) / (N - K))
    return np.sqrt(np.diag(corr_ * XtXi @ meat @ XtXi))

def block_boot(d, y, bcol, B, rng):
    blocks = d[bcol].unique()
    n = len(blocks)
    est = []
    for _ in range(B):
        pick = rng.choice(n, n)
        frames = [d[d[bcol] == blocks[i]] for i in pick]
        dd = pd.concat(frames)
        yy = np.concatenate([y[f.index.values] for f in frames])
        try:
            est.append(fit_rows(dd, yy))
        except Exception:
            pass
    est = np.array(est)
    if len(est) < 30:
        return np.full(4, np.nan), len(est)
    return np.nanstd(est, axis=0), len(est)

def pairs_boot(d, y, B, rng):
    est = []
    for _ in range(B):
        idxs = []
        for _, ii in pd.Series(range(len(d))).groupby(d.country.values).groups.items():
            ii = np.array(list(ii))
            idxs.append(ii[rng.choice(len(ii), len(ii))])
        pick = np.concatenate(idxs)
        dd = d.iloc[pick]
        try:
            est.append(fit_rows(dd, y[pick]))
        except Exception:
            pass
    est = np.array(est)
    if len(est) < 30:
        return np.full(4, np.nan), len(est)
    return np.nanstd(est, axis=0), len(est)

# ---------- distance matrix (km, haversine on degrees approx) ----------
latr = np.radians(dm.lat.values)
dlon = np.radians(dm.lon.values[:, None] - dm.lon.values[None, :])
dlat = latr[:, None] - latr[None, :]
hav = np.sin(dlat / 2) ** 2 + np.cos(latr[:, None]) * np.cos(latr[None, :]) * np.sin(dlon / 2) ** 2
DIST = 6371.0 * 2 * np.arcsin(np.sqrt(np.clip(hav, 0, 1)))

Xcols = np.c_[dm.irr_share_base2000.fillna(0).values, dm.mismatch_T.values]
# design for fitting in sims (X without interaction coefficient matters
# only for residual covariance; build full X)
def build_X(d):
    return np.c_[d.irr_share_base2000.values, d.mismatch_T.values,
                 (d.irr_share_base2000 * d.mismatch_T).values, X0[d.index.values]]
Xfull = build_X(dm)

def run_sims(d, yfun, seed):
    """Return dict of per-method lists of (b3_hat, se)."""
    rng = np.random.default_rng(seed)
    out = {k: [] for k in ("hc3", "crve", "pairs", "grid10", "km")}
    fails = {k: 0 for k in out}
    for rep in range(200):
        y = yfun(rng)
        b = fit_rows(d, y)
        e = y - Xfull @ b
        out["hc3"].append((b[2], hc3(Xfull, y, b)[2]))
        out["crve"].append((b[2], country_crve(Xfull, y, b, d.country.values)[2]))
        se, nb = pairs_boot(d, y, 60, rng)
        out["pairs"].append((b[2], se[2] if np.isfinite(se[2]) else np.nan))
        se, nb = block_boot(d, y, "block_grid10", 60, rng)
        out["grid10"].append((b[2], se[2] if np.isfinite(se[2]) else np.nan))
        se, nb = block_boot(d, y, "block_km", 60, rng)
        out["km"].append((b[2], se[2] if np.isfinite(se[2]) else np.nan))
    return out

scen_rows = []
sd_sp = np.nanstd(dm.irr_share_base2000.values)
sd_m = np.nanstd(dm.mismatch_T.values)
sd_y = np.nanstd(dm.jsd.values)
for rho_km, label in [(1.0, "independent"), (150.0, "weak"),
                      (500.0, "moderate"), (1500.0, "strong")]:
    L = np.linalg.cholesky(np.exp(-DIST / rho_km) * sd_y ** 2 + 1e-9 * np.eye(N))
    def mk(rho_):
        def f(rng):
            # country random effect + spatially correlated residual
            cre = rng.normal(0, sd_y * 0.3, size=dm.country.nunique())
            cmap = {c: i for i, c in enumerate(sorted(dm.country.unique()))}
            return (dm.country.map(cmap).map(lambda i: cre[i]).values
                    + L @ rng.normal(size=N))
        return f
    out = run_sims(dm, mk(rho_km), seed=20261003 + int(rho_km))
    for meth, vals in out.items():
        v = pd.DataFrame(vals, columns=["b3", "se"])
        v = v.dropna()
        rej = (np.abs(v.b3) > 1.96 * v.se).mean()
        cov = np.nan  # null: coverage of 0
        cov = ((v.b3 - 1.96 * v.se <= 0) & (v.b3 + 1.96 * v.se >= 0)).mean()
        scen_rows.append(dict(scenario=label, rho_km=rho_km, method=meth,
                              n_sims=len(v), type_I=float(rej),
                              coverage_null=float(cov),
                              median_ci_width=float((2 * 1.96 * v.se).median()),
                              failure_rate=float(1 - len(v) / 200)))
si = pd.DataFrame(scen_rows)
si.to_csv(FOUT / "analysis" / "spatial_inference_simulation_v2.csv",
          index=False)
print(si.pivot_table(index=["scenario", "method"], values=["type_I", "coverage_null", "median_ci_width"]).round(3).to_string())

# ---------- information simulation v2 ----------
dm2 = dm.dropna(subset=["irr_share_base2000"]).reset_index(drop=True)
Nz = len(dm2)
z_irr = (dm2.irr_share_base2000 - dm2.irr_share_base2000.mean()) / dm2.irr_share_base2000.std()
z_mm = (dm2.mismatch_T - dm2.mismatch_T.mean()) / dm2.mismatch_T.std()
z_int = z_irr * z_mm
ybar, ysd = dm2.jsd.mean(), dm2.jsd.std()
X0z = np.c_[np.ones(Nz), pd.get_dummies(dm2.country, drop_first=True).values.astype(float)]
Xz = np.c_[z_irr.values, z_mm.values, z_int.values, X0z]
latr2 = np.radians(dm2.lat.values)
dlon2 = np.radians(dm2.lon.values[:, None] - dm2.lon.values[None, :])
dlat2 = latr2[:, None] - latr2[None, :]
hav2 = np.sin(dlat2 / 2) ** 2 + np.cos(latr2[:, None]) * np.cos(latr2[None, :]) * np.sin(dlon2 / 2) ** 2
DIST2 = 6371.0 * 2 * np.arcsin(np.sqrt(np.clip(hav2, 0, 1)))
rho0 = 500.0
Lz = np.linalg.cholesky(np.exp(-DIST2 / rho0) * 0.5 ** 2 + 1e-9 * np.eye(Nz))

def gen(rng, b3):
    # bounded outcome: fractional-logit DGP on JSD scale
    lin = (0.1 * z_irr.values - 0.05 * z_mm.values + b3 * z_int.values
           + Lz @ rng.normal(size=Nz))
    lam = np.clip(dm2.jsd.values + lin, 1e-4, 0.95)
    return lam

def fitz(d, y):
    b, *_ = np.linalg.lstsq(Xz, y, rcond=None)
    return b

def block_boot_z(d, bcol, y, B, rng):
    blocks = d[bcol].unique()
    n_ = len(blocks)
    est = []
    for _ in range(B):
        pick = rng.choice(n_, n_)
        rows_ = np.concatenate([np.where(d[bcol].values == blocks[i])[0] for i in pick])
        dd = d.iloc[rows_]
        Xr = np.c_[z_irr.values[dd.index.values],
                   z_mm.values[dd.index.values],
                   z_int.values[dd.index.values],
                   X0z[dd.index.values]]
        try:
            bb, *_ = np.linalg.lstsq(Xr, y[rows_], rcond=None)
            est.append(bb[2])
        except Exception:
            pass
    est = np.array(est)
    return (np.nanstd(est) if len(est) >= 30 else np.nan), len(est)

info_rows = []
for true_b3, lab in [(0.0, "null"), (0.25, "small"),
                     (0.50, "moderate"), (0.75, "large")]:
    rng = np.random.default_rng(777 + int(true_b3 * 100))
    ests, ses, okf = [], [], 0
    for rep in range(150):
        y = gen(rng, true_b3)
        b = fitz(dm2, y)
        se, nb = block_boot_z(dm2, "block_grid10", y, 60, rng)
        ests.append(b[2]); ses.append(se); okf += nb < 60
    ests = np.array(ests); ses = np.array(ses)
    good = np.isfinite(ses)
    info_rows.append(dict(true_beta3=true_b3, label=lab, n_sims=int(good.sum()),
        bias=float(ests[good].mean() - true_b3),
        rmse=float(np.sqrt(((ests[good] - true_b3) ** 2).mean())),
        type_I=float((np.abs(ests[good]) > 1.96 * ses[good]).mean()) if true_b3 == 0 else np.nan,
        coverage=float(((ests[good] - 1.96 * ses[good] <= true_b3) & (ests[good] + 1.96 * ses[good] >= true_b3)).mean()),
        power=float((np.abs(ests[good]) > 1.96 * ses[good]).mean()) if true_b3 != 0 else np.nan,
        median_ci_width=float(np.median(2 * 1.96 * ses[good])),
        boot_fail_rate=float(1 - good.mean())))
ir = pd.DataFrame(info_rows)
ir.to_csv(FOUT / "analysis" / "information_simulation_v2.csv", index=False)
print(ir.round(3).to_string())
