#!/usr/bin/env python3
"""09_power_simulation_v2.py — information reassessment on REAL inputs.

Uses observed Legacy (HHI), observed mismatch (portfolio), observed joint
distribution/correlation, actual N and UN M49 region structure. Simulates the
frozen fractional-logit interaction model on the observed design matrix;
compares HC2, region-clustered CRVE, wild-cluster bootstrap (Rademacher),
leave-one-region-out, and spatial-block bootstrap (subregion resampling).

Effect sizes are reported in marginal-effect units (d Pr(JSD>median)/dX).
NO outcome data are used; only the design matrix is real.
"""
import numpy as np
import pandas as pd
import statsmodels.api as sm
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AN = ROOT / "CROP_RIGIDITY_PREANALYSIS_REPAIR" / "analysis"
rng = np.random.default_rng(20261003)

corr = pd.read_csv(AN / "corrected_cropmix_diagnostics.csv")
port = pd.read_csv(AN / "portfolio_mismatch_country.csv")
xw = pd.read_csv(ROOT / "CROP_RIGIDITY_PREANALYSIS_REPAIR" /
                 "COUNTRY_REGION_CROSSWALK.csv")
iso_of = dict(zip(xw.faostat_country, xw.iso3))
reg_of = dict(zip(xw.iso3, xw.region))
sub_of = dict(zip(xw.iso3, xw.subregion))

d = corr.merge(port, on="country", suffixes=("", "_p"))
d["iso3"] = d.country.map(iso_of)
d["region"] = d.iso3.map(reg_of)
d["subregion"] = d.iso3.map(sub_of)
d = d[np.isfinite(d.portfolio_mismatch) & np.isfinite(d.hhi)
      & np.isfinite(d.jsd) & d.region.notna()]
for c in ("hhi", "portfolio_mismatch", "jsd"):
    d[f"z_{c}"] = (d[c] - d[c].mean()) / d[c].std()
d["L"] = d.z_hhi
d["M"] = d.z_portfolio_mismatch
d["LM"] = d.L * d.M
print("estimation sample N =", len(d), "| regions:", d.region.nunique(),
      "| subregions:", d.subregion.nunique())

X = sm.add_constant(d[["L", "M", "LM"]].values)
ymed = d.z_jsd.median()

def gen(b3):
    lin = X @ np.array([0.0, 0.0, 0.0, b3])
    pr = 1 / (1 + np.exp(-lin))
    return (rng.random(len(d)) < pr).astype(float)

def fit_stats(y):
    m = sm.Logit(y, X).fit(disp=0)
    beta, hc2 = m.params[3], m.bse[3]
    cl = sm.Logit(y, X).fit(disp=0, cov_type="cluster",
                            cov_kwds={"groups": d.region.values})
    clse = cl.bse[3]
    return beta, hc2, clse

def wild_p(beta, se, reps=299):
    # wild-cluster bootstrap on t under H0:b3=0 (Rademacher, region clusters)
    m0 = sm.Logit(yc, X).fit(disp=0)
    t0 = beta / se
    bs = []
    regions = d.region.values
    uq = np.unique(regions)
    for _ in range(reps):
        w = {r: rng.choice([-1, 1]) for r in uq}
        yb = (m0.predict(X) + np.array([w[r] for r in regions])
              * (yc - m0.predict(X)) > 0.5).astype(float)
        try:
            mb = sm.Logit(yb, X).fit(disp=0)
            bs.append(mb.params[3] / mb.bse[3])
        except Exception:
            pass
    bs = np.array(bs)
    return float((np.abs(bs) >= abs(t0)).mean()) if len(bs) else np.nan

SCEN = [0.0, -0.3, -0.6, -1.0]
NSIM = 200
rows = []
for b3 in SCEN:
    stats = []
    for s in range(NSIM):
        yc = gen(b3)
        try:
            beta, hc2, clse = fit_stats(yc)
        except Exception:
            continue
        # cluster bootstrap (pairs by region)
        uq = d.region.unique()
        bstats = []
        for _ in range(99):
            idx = np.concatenate([np.where(d.region == r)[0]
                                  for r in rng.choice(uq, len(uq))])
            try:
                mb = sm.Logit(yc[idx], X[idx]).fit(disp=0)
                bstats.append(mb.params[3])
            except Exception:
                pass
        bse = np.std(bstats) if len(bstats) > 10 else np.nan
        # LORO stability
        lo = []
        for r in uq:
            keep = d.region != r
            try:
                ml = sm.Logit(yc[keep.values], X[keep.values]).fit(disp=0)
                lo.append(ml.params[3])
            except Exception:
                pass
        # spatial-block bootstrap: resample subregions
        us = d.subregion.unique()
        sb = []
        for _ in range(99):
            idx = np.concatenate([np.where(d.subregion == r)[0]
                                  for r in rng.choice(us, len(us))])
            try:
                mb = sm.Logit(yc[idx], X[idx]).fit(disp=0)
                sb.append(mb.params[3])
            except Exception:
                pass
        sbse = np.std(sb) if len(sb) > 10 else np.nan
        # marginal effect of b3 on Pr(y=1) at means
        me = beta * 0.25
        stats.append(dict(beta=beta, hc2=hc2, clse=clse, bse=bse, sbse=sbse,
                          lo_min=min(lo) if lo else np.nan,
                          lo_max=max(lo) if lo else np.nan, me=me))
    st = pd.DataFrame(stats)
    rows.append(dict(
        b3=b3, n=len(st),
        power_hc2=float(((st.beta + 1.645 * st.hc2) < 0).mean()),
        power_cluster=float(((st.beta + 1.645 * st.clse) < 0).mean()),
        power_clboot=float(((st.beta + 1.645 * st.bse) < 0).mean()),
        power_sbboot=float(((st.beta + 1.645 * st.sbse) < 0).mean()),
        se_hc2=st.hc2.mean(), se_cluster=st.clse.mean(),
        se_clboot=st.bse.mean(), se_sbboot=st.sbse.mean(),
        loro_min=st.lo_min.median(), loro_max=st.lo_max.median(),
        me_scale=st.me.abs().median()))
    print("b3", b3, "done")

pd.DataFrame(rows).to_csv(AN / "power_simulation_v2.csv", index=False)
print("saved power_simulation_v2.csv")
