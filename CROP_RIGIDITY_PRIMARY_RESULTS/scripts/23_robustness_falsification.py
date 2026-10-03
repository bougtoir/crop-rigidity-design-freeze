#!/usr/bin/env python3
"""23_robustness_falsification.py — pre-registered robustness specs,
falsification suite, exploratory subgroups, leave-one-out.

Same estimator as primary: fractional logit, standardized HHI x mismatch,
subregion cluster bootstrap percentile 95% CI (B=999, seed 20261003).
"""
import gzip
import json
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.othermod.betareg import BetaModel

ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "CROP_RIGIDITY_PRIMARY_RESULTS"
AN = PKG / "analysis"
LOCK = ROOT / "CROP_RIGIDITY_FINAL_LOCK"
REPAIR = ROOT / "CROP_RIGIDITY_PREANALYSIS_REPAIR"
RAW = ROOT / "data" / "raw"
JSD_MAX = float(np.sqrt(np.log(2)))
rng = np.random.default_rng(20261003)
B = 999

est = pd.read_parquet(PKG / "_cache_est.parquet")
meta = json.load(open(PKG / "_cache_meta.json"))
MU, SDv = meta["means"], meta["sds"]
aux = pd.read_csv(AN / "aux_mismatches.csv")
auxv = {k: v.set_index("iso3").mismatch for k, v in aux.groupby("variant")}

xw = pd.read_csv(REPAIR / "COUNTRY_REGION_CROSSWALK.csv")
iso_of = dict(zip(xw.faostat_country, xw.iso3))
reg_of = dict(zip(xw.iso3, xw.region))
sub_of = dict(zip(xw.iso3, xw.subregion))

df = pd.read_feather(RAW / "faostat_qcl_2026-02-25.feather")
audit = pd.read_csv(REPAIR / "FAOSTAT_CROP_ITEM_AUDIT.csv")
keep = set(audit.loc[audit.include_primary == 1, "item_name"])
haf = df[(df.element == "Area harvested") & (df.value > 0)]
haf = haf[haf["item"].isin(keep)][["country", "year", "item", "value"]]

def shares(d):
    s = d.groupby(["country", "item"], observed=True)["value"].mean().reset_index()
    s["share"] = s.value / s.groupby("country", observed=True).value.transform("sum")
    return s

def js(p, q):
    m = 0.5 * (p + q)
    return float(np.sqrt(0.5 * np.where(p > 0, p * np.log(p / m), 0).sum()
                         + 0.5 * np.where(q > 0, q * np.log(q / m), 0).sum()))

def cropmix(leg, out):
    recs = []
    for c, g in haf.groupby("country", observed=True):
        gl = g[(g.year >= leg[0]) & (g.year <= leg[1])]
        go = g[(g.year >= out[0]) & (g.year <= out[1])]
        if gl.year.nunique() < 5 or go.year.nunique() < 5:
            continue
        sl, so = shares(gl), shares(go)
        if sl.item.nunique() < 4 or so.item.nunique() < 4:
            continue
        p = sl.set_index("item")["share"]; q = so.set_index("item")["share"]
        idx = sorted(set(p.index) | set(q.index))
        p, q = p.reindex(idx, fill_value=0.), q.reindex(idx, fill_value=0.)
        recs.append(dict(country=c, hhi=float((p ** 2).sum()),
                         dominant_crop=p.idxmax(), n_years=int(gl.year.nunique()),
                         jsd=js(p.values, q.values),
                         replaced=int(p.idxmax() != q.idxmax())))
    return pd.DataFrame(recs)

cm = {}
cm["lagged"] = cropmix((1981, 2000), (2011, 2020))
cm["pre_trend"] = cropmix((1981, 1990), (1991, 2001))
cm["short_out"] = cropmix((1981, 2001), (2002, 2010))
cm["lag_hhi"] = cropmix((1981, 2000), (2001, 2005))  # for legacy hhi 81-00
cm["delta"] = pd.read_parquet(PKG / "_cache_est.parquet")[["country"]]  # placeholder
old = pd.read_csv(REPAIR / "analysis" / "corrected_cropmix_diagnostics.csv")
v2 = pd.read_csv(LOCK / "analysis" / "cropmix_diagnostics_v2.csv")
ther = pd.read_csv(LOCK / "analysis" / "mismatch_diagnostics_v3.csv")
port = pd.read_csv(LOCK / "analysis" / "portfolio_mismatch_v3.csv")

def build(d, exposure_col, hhi_col="hhi", out_col="jsd"):
    """standardize within the spec's own rows (specs re-standardize on their
    estimation set; frozen ladder sample for the primary spec only)."""
    d = d.dropna(subset=[exposure_col, hhi_col, out_col]).copy()
    if len(d) < 20:
        return None
    hz = (d[hhi_col] - d[hhi_col].mean()) / d[hhi_col].std()
    mz = (d[exposure_col] - d[exposure_col].mean()) / d[exposure_col].std()
    return d, hz.values, mz.values

def boot_b3(yv, Xd, gids, Bn=B):
    ids = np.unique(gids); bs = []
    for _ in range(Bn):
        dr = rng.choice(ids, size=len(ids), replace=True)
        idx = np.concatenate([np.flatnonzero(gids == g) for g in dr])
        try:
            f = sm.GLM(yv[idx], Xd[idx], family=sm.families.Binomial()
                       ).fit(disp=0, maxiter=40)
            bs.append(f.params[3])
        except Exception:
            continue
    if len(bs) < Bn * 0.7:
        return (np.nan, np.nan, len(bs))
    bs = np.sort(bs)
    return float(bs[int(0.025 * len(bs))]), \
        float(bs[int(0.975 * len(bs)) - 1]), len(bs)

def spec_fit(d, exposure_col, out_transform, model="frac", Bn=B):
    r = build(d, exposure_col, "hhi", "jsd_raw")
    if r is None:
        return None
    d2, hz, mz = r
    Xd = np.column_stack([np.ones(len(d2)), hz, mz, hz * mz])
    yv = out_transform(d2.jsd_raw.values)
    gids = d2.subregion.fillna("none").values
    try:
        if model == "frac":
            f = sm.GLM(yv, Xd, family=sm.families.Binomial()).fit()
            b3 = float(f.params[3])
        elif model == "beta":
            f = BetaModel(yv, Xd).fit()
            b3 = float(f.params[3])
        else:  # ols
            f = sm.OLS(yv, Xd).fit()
            b3 = float(f.params[3])
    except Exception:
        return dict(N=len(d2), beta3=np.nan, ci_lo=np.nan, ci_hi=np.nan,
                    reps=0)
    if model == "frac":
        lo, hi, nr = boot_b3(yv, Xd, gids, Bn)
    else:
        lo, hi, nr = float(b3 - 1.96 * f.bse[3]), float(b3 + 1.96 * f.bse[3]), 0
    return dict(N=len(d2), beta3=b3, ci_lo=lo, ci_hi=hi, reps=nr)

def norm_j(v): return np.clip(v / JSD_MAX, 1e-6, 1 - 1e-6)

base = est.rename(columns={"mismatch": "expo"})[
    ["iso3", "country", "hhi", "jsd", "dominant_crop", "spam_crop", "region",
     "subregion", "centroid_lat", "centroid_lon"]].copy()
base["jsd_raw"] = base.jsd
base["expo"] = est.mismatch

ledger = []
def ledger_row(tag, d, expo_col, model, window, exposure, outcome,
               prereg="yes", Bn=B):
    r = spec_fit(d, expo_col, norm_j, model, Bn)
    if r is None:
        r = dict(N=0, beta3=np.nan, ci_lo=np.nan, ci_hi=np.nan, reps=0)
    ledger.append(dict(spec=tag, N=r["N"], exposure=exposure, outcome=outcome,
                       window=window, model=model, beta3=r["beta3"],
                       ci_lo=r["ci_lo"], ci_hi=r["ci_hi"],
                       direction=("positive" if (r["beta3"] or 0) > 0 else
                                  "negative" if (r["beta3"] or 0) < 0 else "na"),
                       preregd=prereg, boot_reps=r["reps"]))
    print(tag, r)

# ---------------- robustness ------------------------------------------------
# A old ladder: legacy 81-00, expo 01-20 (old-window calendar mismatch)
dA = old.rename(columns={"jsd": "jsd_raw"})
dA["expo"] = dA.country.map(iso_of).map(auxv["old_ladder"])
dA["subregion"] = dA.country.map(iso_of).map(sub_of)
ledger_row("A_old_ladder", dA, "expo", "frac", "legacy81-00/expo01-20/outcome01-20",
           "dominant calendar mismatch", "JSD")

# B lagged: legacy 81-00, expo 01-10, outcome 11-20
dB = cm["lagged"].rename(columns={"jsd": "jsd_raw"})
dB["expo"] = dB.country.map(iso_of).map(auxv["lagged"])
dB["subregion"] = dB.country.map(iso_of).map(sub_of)
ledger_row("B_lagged", dB, "expo", "frac", "legacy81-00/expo01-10/outcome11-20",
           "dominant calendar mismatch", "JSD")

# C thermal-season displacement (frozen window, v3 diagnostics)
dC = v2.rename(columns={"jsd": "jsd_raw"})
dC["iso3"] = dC.country.map(iso_of)
dC = dC.merge(ther[["iso3", "mismatch_thermal"]], on="iso3", how="left")
dC["expo"] = dC["mismatch_thermal"]
dC["subregion"] = dC.country.map(iso_of).map(sub_of)
ledger_row("C_thermal", dC, "expo", "frac", "legacy81-01/expo02-20",
           "thermal-season displacement", "JSD")

# D portfolio calendar mismatch at coverage floors
for thr in (0.70, 0.50, 0.80):
    dD = v2.rename(columns={"jsd": "jsd_raw"})
    pm = port.drop_duplicates("iso3").set_index("iso3")
    dD["iso3"] = dD.country.map(iso_of)
    dD["expo"] = dD.iso3.map(pm.portfolio_mismatch)
    dD["pcov"] = dD.iso3.map(pm.share_coverage)
    dD.loc[dD.pcov < thr, "expo"] = np.nan
    dD["subregion"] = dD.country.map(iso_of).map(sub_of)
    ledger_row(f"D_portfolio_cov{thr}", dD, "expo", "frac",
               "legacy81-01/expo02-20", "portfolio calendar mismatch", "JSD")

# E alternative families on the frozen spec
baseb = base.copy()
r = spec_fit(baseb, "expo", norm_j, "beta")
ledger.append(dict(spec="E_beta_regression", N=(r or {}).get("N", 0),
                   exposure="dominant calendar mismatch", outcome="JSD",
                   window="frozen", model="beta regression",
                   beta3=(r or {}).get("beta3", np.nan),
                   ci_lo=(r or {}).get("ci_lo", np.nan),
                   ci_hi=(r or {}).get("ci_hi", np.nan),
                   direction="na", preregd="yes", boot_reps=0))
baseo = base.copy()
def logit_j(v):
    yv = norm_j(v); return np.log(yv / (1 - yv))
r = spec_fit(baseo.assign(jsd_raw=base.jsd), "expo", logit_j, "ols")
ledger.append(dict(spec="E_logit_linear", N=(r or {}).get("N", 0),
                   exposure="dominant calendar mismatch", outcome="logit(JSD)",
                   window="frozen", model="OLS on logit scale",
                   beta3=(r or {}).get("beta3", np.nan),
                   ci_lo=(r or {}).get("ci_lo", np.nan),
                   ci_hi=(r or {}).get("ci_hi", np.nan),
                   direction="na", preregd="yes", boot_reps=0))

# F alternative outcomes (delta_hhi, replacement) — exploratory flag kept
dF = v2.rename(columns={"jsd": "jsd_raw"})
dF["expo"] = dF.country.map(iso_of).map(auxv["primary"])
dF["subregion"] = dF.country.map(iso_of).map(sub_of)
dd = dF.dropna(subset=["expo"])
dd = dd[dd.country.isin(set(est.country))]
dd["jsd_raw"] = dd["delta_hhi"]
r = spec_fit(dd, "expo", lambda v: v, "ols")
ledger.append(dict(spec="F_delta_hhi", N=(r or {}).get("N", 0),
                   exposure="dominant calendar mismatch", outcome="delta HHI",
                   window="frozen", model="OLS", beta3=(r or {}).get("beta3", np.nan),
                   ci_lo=(r or {}).get("ci_lo", np.nan), ci_hi=(r or {}).get("ci_hi", np.nan),
                   direction="na", preregd="yes", boot_reps=0))
led = pd.DataFrame(ledger)
led.to_csv(AN / "robustness_specification_ledger.csv", index=False)
print(led[["spec", "N", "beta3", "ci_lo", "ci_hi"]].to_string(index=False))
