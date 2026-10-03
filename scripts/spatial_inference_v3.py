#!/usr/bin/env python3
"""V3 spatial blocks + inference validation on the locked primary sample.

Rebuilds geographic blocks (10deg grid + within-country kmeans) on
PRIMARY_SUBNATIONAL_SAMPLE_LOCKED.csv and re-runs the type-I calibration
under exponentially correlated spatial residuals (rho = 1/150/500/1500 km),
with country random effects. Estimator: OLS + country FE (frozen).
Output: analysis/admin_spatial_blocks_v3.csv,
        analysis/admin_spatial_blocks_v3_describe.csv,
        analysis/spatial_inference_simulation_v3.csv
"""
import numpy as np
import pandas as pd
import geopandas as gpd
from pathlib import Path
from scipy.cluster.vq import kmeans2

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "SUBNATIONAL_RIGIDITY_DESIGN_FREEZE"
V3 = ROOT / "SUBNATIONAL_RIGIDITY_LOCK_V3"
RAW = ROOT / "data" / "raw"
dm = pd.read_csv(V3 / "analysis" / "PRIMARY_SUBNATIONAL_SAMPLE_LOCKED.csv")
xw = pd.read_csv(OUT / "ADMIN_BOUNDARY_CROSSWALK.csv")

gadm = gpd.read_file(RAW / "gadm410" / "gadm_410-levels.gpkg", layer="ADM_1",
                     columns=["GID_1"])
gid2geom = dict(zip(gadm["GID_1"], gadm.geometry))
nuts = {}
for lvl in (1, 2):
    g = gpd.read_file(RAW / "subnat" / f"nuts2021_l{lvl}.geojson")
    nuts.update(dict(zip(g.NUTS_ID, g.geometry)))
for lvl in (1, 2):
    g = gpd.read_file(RAW / "subnat" / f"nuts2016_l{lvl}.geojson")
    nuts.update({k: v for k, v in zip(g.NUTS_ID, g.geometry)
                 if k not in nuts})
for lvl in (1, 2):
    g = gpd.read_file(RAW / "subnat" / f"nuts2010_l{lvl}.geojson")
    nuts.update({k: v for k, v in zip(g.NUTS_ID, g.geometry)
                 if k not in nuts})
hv = gpd.read_file(RAW / "subnat" / "hvstat_africa_boundary_v1.2.gpkg")
hv["_key"] = ("HV1:" + hv["country_code"].astype(str) + ":"
              + hv["admin_1"].fillna("").astype(str))
hv_units = {k: s.union_all() for k, s in
            hv[hv["admin_1"].notna()].groupby("_key")}
del gadm
gid_of = xw.drop_duplicates("unit_id").set_index("unit_id")["gadm41_gid"]


def geom_of(uid):
    gid = gid_of.get(uid)
    if pd.notna(gid) and gid in gid2geom:
        return gid2geom[gid]
    if uid in hv_units:
        return hv_units[uid]
    return nuts.get(uid)


lon, lat = {}, {}
for uid in dm.unit_id.unique():
    g = geom_of(uid)
    if g is not None:
        c = g.centroid
        lon[uid], lat[uid] = c.x, c.y
dm["lon"] = dm.unit_id.map(lon)
dm["lat"] = dm.unit_id.map(lat)
dm = dm.dropna(subset=["lon"]).reset_index(drop=True)
N = len(dm)
print("units:", N, "countries:", dm.country.nunique())


def grid_block(lon_, lat_, size):
    return (np.floor(lon_ / size).astype(int).astype(str) + ":"
            + np.floor(lat_ / size).astype(int).astype(str))


dm["block_grid10"] = grid_block(dm.lon, dm.lat, 10.0)
dm["block_grid15"] = grid_block(dm.lon, dm.lat, 15.0)
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
for col in ("block_grid10", "block_grid15", "block_km"):
    g = dm.groupby(col)
    sz = g.size()
    rows.append(dict(scheme=col, n_blocks=int(sz.size),
                     units_per_block_med=float(sz.median()),
                     units_per_block_max=int(sz.max()),
                     singleton_blocks=int((sz == 1).sum()),
                     countries_crossed=int((g["country"].nunique() > 1).sum())))
blk_desc = pd.DataFrame(rows)
dm[["unit_id", "country", "lon", "lat", "block_grid10", "block_grid15",
    "block_km"]].to_csv(V3 / "analysis" / "admin_spatial_blocks_v3.csv",
                        index=False)
blk_desc.to_csv(V3 / "analysis" / "admin_spatial_blocks_v3_describe.csv",
                index=False)
print(blk_desc.to_string())

X0 = np.c_[np.ones(N), pd.get_dummies(dm.country, drop_first=True).values.astype(float)]
Xfull = np.c_[dm.irr_share_base2000.values, dm.mismatch_T.values,
              (dm.irr_share_base2000 * dm.mismatch_T).values, X0]


def fit_rows(d, y, idx=None):
    if idx is None:
        idx = d.index.values
    X = np.c_[d.irr_share_base2000.values, d.mismatch_T.values,
              (d.irr_share_base2000 * d.mismatch_T).values, X0[idx]]
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
    e = y - X @ b
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
    ublocks = d[bcol].unique()
    nb = len(ublocks)
    pos = {u: np.where(d[bcol].values == u)[0] for u in ublocks}
    est = []
    for _ in range(B):
        pick = rng.choice(nb, nb)
        rows_ = np.concatenate([pos[ublocks[i]] for i in pick])
        dd = d.iloc[rows_]
        yy = y[rows_]
        try:
            Xr = np.c_[dd.irr_share_base2000.values, dd.mismatch_T.values,
                       (dd.irr_share_base2000 * dd.mismatch_T).values,
                       X0[rows_]]
            bb, *_ = np.linalg.lstsq(Xr, yy, rcond=None)
            est.append(bb[:3])
        except Exception:
            pass
    est = np.array(est)
    if len(est) < 30:
        return np.nan, len(est)
    return np.nanstd(est[:, 2]), len(est)


latr = np.radians(dm.lat.values)
dlon = np.radians(dm.lon.values[:, None] - dm.lon.values[None, :])
dlat = latr[:, None] - latr[None, :]
hav = (np.sin(dlat / 2) ** 2
       + np.cos(latr[:, None]) * np.cos(latr[None, :])
       * np.sin(dlon / 2) ** 2)
DIST = 6371.0 * 2 * np.arcsin(np.sqrt(np.clip(hav, 0, 1)))
sd_y = float(np.nanstd(dm.jsd.values))
cmap = {c: i for i, c in enumerate(sorted(dm.country.unique()))}
cidx = dm.country.map(cmap).values

scen_rows = []
for rho_km, label in [(1.0, "independent"), (150.0, "weak"),
                      (500.0, "moderate"), (1500.0, "strong")]:
    L = np.linalg.cholesky(np.exp(-DIST / rho_km) * sd_y ** 2
                           + 1e-9 * np.eye(N))
    rng = np.random.default_rng(20261003 + int(rho_km))
    res = {k: [] for k in ("hc3", "crve_country", "grid10", "grid15", "km")}
    for rep in range(200):
        cre = rng.normal(0, sd_y * 0.3, size=len(cmap))
        y = cre[cidx] + L @ rng.normal(size=N)
        b = fit_rows(dm, y)
        res["hc3"].append((b[2], hc3(Xfull, y, b)[2]))
        res["crve_country"].append(
            (b[2], country_crve(Xfull, y, b, dm.country.values)[2]))
        for bcol in ("grid10", "grid15", "km"):
            se, nb = block_boot(dm, y, "block_" + bcol, 60, rng)
            res[bcol].append((b[2], se))
    for meth, vals in res.items():
        v = pd.DataFrame(vals, columns=["b3", "se"]).dropna()
        rej = float((np.abs(v.b3) > 1.96 * v.se).mean())
        cov = float(((v.b3 - 1.96 * v.se <= 0)
                     & (v.b3 + 1.96 * v.se >= 0)).mean())
        calib = ("PASS" if rej <= 0.07
                 else "WARNING" if rej <= 0.10 else "FAIL")
        scen_rows.append(dict(scenario=label, rho_km=rho_km, method=meth,
                              n_sims=len(v), type_I=rej,
                              coverage_null=cov,
                              median_ci_width=float((2 * 1.96 * v.se).median()),
                              calibration=calib))
si = pd.DataFrame(scen_rows)
si.to_csv(V3 / "analysis" / "spatial_inference_simulation_v3.csv",
          index=False)
print(si.to_string(index=False))
