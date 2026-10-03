#!/usr/bin/env python3
"""08_build_mismatch.py — Mahalanobis climate mismatch on real data.

Per country:
  dominant crop = largest legacy (1981-2000) FAOSTAT harvested-area share
  footprint     = SPAM2000 occupied cells of the corresponding SPAM class
  climate       = NASA POWER monthly T2M/PRECTOTCORR in footprint cells
  growing season= months whose cell climatological mean T2M (1984-2000) > 5 C
  baseline      = growing-season (T_mean, P_total) per cell-year, 1984-2000
  exposure      = same per cell-year, 2001-2020
  mismatch      = sqrt( (mu_e - mu_b)' Sigma_b^-1 (mu_e - mu_b) ),
                  Sigma_b shrunk toward diagonal with a single common rule
                  (Ledoit-Wolf shrinkage intensity estimated per country on
                  the SAME formula for all countries; no per-country tuning).

Outputs:
  analysis/primary_mismatch_country.csv
  analysis/mismatch_diagnostics.csv
  analysis/portfolio_mismatch_country.csv  (for Issue 3 comparison)
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.covariance import LedoitWolf

ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "CROP_RIGIDITY_PREANALYSIS_REPAIR"
AN = PKG / "analysis"
RAW = ROOT / "data" / "raw"
BASE = (1984, 2000)
EXPO = (2001, 2020)

corr = pd.read_csv(AN / "corrected_cropmix_diagnostics.csv")
xw = pd.read_csv(PKG / "COUNTRY_REGION_CROSSWALK.csv")
sxw = pd.read_csv(PKG / "SPAM_FAOSTAT_CROSSWALK.csv")
fc = pd.read_csv(AN / "footprint_cells.csv")
name2spam = dict(zip(sxw.item_name, sxw.spam_crop))
iso_of = dict(zip(xw.faostat_country, xw.iso3))
region_of = dict(zip(xw.iso3, xw.region))
sub_of = dict(zip(xw.iso3, xw.subregion))

# legacy shares for portfolio weights (baseline mix shares by SPAM class)
df = pd.read_feather(RAW / "faostat_qcl_2026-02-25.feather")
ha = df[(df.element == "Area harvested") & (df.value > 0)]
ha = ha[(ha.year >= 1981) & (ha.year <= 2000)]
audit = pd.read_csv(PKG / "FAOSTAT_CROP_ITEM_AUDIT.csv")
keep = set(audit.loc[audit.include_primary == 1, "item_name"])
ha = ha[ha["item"].isin(keep)]
shares = (ha.groupby(["country", "item"], observed=True)["value"].mean()
          .reset_index())
shares["share"] = shares.value / shares.groupby("country", observed=True).value.transform("sum")
shares["spam_crop"] = shares.item.map(name2spam)

def load_climate(iso):
    p = RAW / "power" / f"{iso}.parquet"
    if not p.exists():
        return None
    d = pd.read_parquet(p)
    d["lon"] = d.lon.round(3); d["lat"] = d.lat.round(3)
    d["year"] = (d.ym // 100).astype(int)
    d["month"] = (d.ym % 100).astype(int)
    return d

_SEASONAL = {}

def seasonal_tables(iso):
    """Per-cell-year growing-season (T,P) for baseline and exposure.
    Growing months are cell-specific: months whose climatological mean T2M
    over the baseline exceeds 5 C. Crop-independent -> computed once."""
    if iso in _SEASONAL:
        return _SEASONAL[iso]
    d = load_climate(iso)
    if d is None:
        _SEASONAL[iso] = (None, None, None)
        return _SEASONAL[iso]
    base = d[(d.year >= BASE[0]) & (d.year <= BASE[1])]
    clim = base.groupby(["lon", "lat", "month"])["t2m"].mean().reset_index()
    gmonths = clim[clim.t2m > 5].groupby(["lon", "lat"])["month"].apply(set)

    def seasonal(dd):
        dd = dd.merge(gmonths.rename("gm"), left_on=["lon", "lat"],
                      right_index=True)
        dd = dd[[m in g for m, g in zip(dd.month, dd.gm)]]
        return dd.groupby(["lon", "lat", "year"]).agg(
            t=("t2m", "mean"), p=("prec", "sum")).reset_index()

    nan_frac = float(d[["t2m", "prec"]].isna().any(axis=1).mean())
    out = (seasonal(base),
           seasonal(d[(d.year >= EXPO[0]) & (d.year <= EXPO[1])]),
           nan_frac)
    _SEASONAL[iso] = out
    return out

def mismatch_for(iso, crop):
    rows = fc[(fc.iso3 == iso) & (fc.spam_crop == crop)]
    if rows.empty:
        return None
    cells = set()
    for j in rows.cells_json:
        cells.update(map(tuple, json.loads(j)))
    b, e, nan_frac = seasonal_tables(iso)
    if b is None:
        return None
    have = set(zip(b.lon, b.lat)) | set(zip(e.lon, e.lat))
    cells = cells & have
    if not cells:
        return None
    b = b[b.set_index(["lon", "lat"]).index.isin(cells)]
    e = e[e.set_index(["lon", "lat"]).index.isin(cells)]
    ncell = len(cells)
    miss = nan_frac
    if len(b) < 10 or len(e) < 10:
        return dict(iso3=iso, crop=crop, mismatch=np.nan, n_cells=ncell,
                    miss=miss, cond=np.nan, det=np.nan, reg="insufficient obs")
    X = b[["t", "p"]].values
    mu_b = X.mean(0)
    cov = LedoitWolf().fit(X)
    S = cov.covariance_
    shrink = float(cov.shrinkage_)
    mu_e = e[["t", "p"]].values.mean(0)
    diff = mu_e - mu_b
    try:
        D = float(np.sqrt(diff @ np.linalg.solve(S, diff)))
        cond = float(np.linalg.cond(S))
        det = float(np.linalg.det(S))
    except np.linalg.LinAlgError:
        D, cond, det = np.nan, np.inf, 0.0
    return dict(iso3=iso, crop=crop, mismatch=D, n_cells=ncell,
                miss=miss, cond=cond, det=det, shrinkage=shrink,
                reg="ledoit-wolf common rule")

dom, port, diag = [], [], []
for _, r in corr.iterrows():
    iso = iso_of.get(r.country)
    if not iso or iso == "none":
        continue
    dcrop = name2spam.get(r.dominant_crop, "none")
    res = mismatch_for(iso, dcrop)
    dres = {} if res is None else res
    dres.pop("iso3", None); dres.pop("crop", None)
    diag.append(dict(iso3=iso, country=r.country, dominant_crop=r.dominant_crop,
                     spam_crop=dcrop, **dres))
    # portfolio: all crops with SPAM class and share>0
    ss = shares[shares.country == r.country]
    ss = ss[ss.spam_crop.notna() & (ss.spam_crop != "none")]
    ss = ss.groupby("spam_crop")["share"].sum()
    ss = ss / ss.sum()
    val, wsum = 0.0, 0.0
    for crop, w in ss.items():
        rr = mismatch_for(iso, crop)
        if rr is not None and np.isfinite(rr.get("mismatch", np.nan)):
            val += w * rr["mismatch"]; wsum += w
    port.append(dict(iso3=iso, country=r.country,
                     portfolio_mismatch=(val / wsum if wsum else np.nan),
                     share_coverage=wsum,
                     dominant_mismatch=(res["mismatch"] if res else np.nan)))
    dom.append(dict(iso3=iso, country=r.country,
                    mismatch=(res["mismatch"] if res else np.nan)))

pd.DataFrame(dom).to_csv(AN / "primary_mismatch_country.csv", index=False)
pd.DataFrame(port).to_csv(AN / "portfolio_mismatch_country.csv", index=False)
pd.DataFrame(diag).to_csv(AN / "mismatch_diagnostics.csv", index=False)
print("done", len(dom))
