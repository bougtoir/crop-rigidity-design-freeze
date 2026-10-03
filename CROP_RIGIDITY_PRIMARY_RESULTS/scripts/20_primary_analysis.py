#!/usr/bin/env python3
"""20_primary_analysis.py — FIRST opening of beta3 under PRIMARY_ANALYSIS_LOCK.

Phases executed strictly in order; the lock file is never modified.
"""
import hashlib
import json
import gzip
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from sklearn.covariance import LedoitWolf

ROOT = Path(__file__).resolve().parents[1]
LOCKPKG = ROOT / "CROP_RIGIDITY_FINAL_LOCK"
PKG = ROOT / "CROP_RIGIDITY_PRIMARY_RESULTS"
AN = PKG / "analysis"; FIG = PKG / "figures"
for d in (AN, FIG): d.mkdir(parents=True, exist_ok=True)
RAW = ROOT / "data" / "raw"
REPAIR = ROOT / "CROP_RIGIDITY_PREANALYSIS_REPAIR"
JSD_MAX = float(np.sqrt(np.log(2)))
SEED = 20261003

# ---- PHASE 0 -------------------------------------------------------------
lock_file = LOCKPKG / "PRIMARY_ANALYSIS_LOCK.yaml"
lock_sha = hashlib.sha256(lock_file.read_bytes()).hexdigest()
expected = (LOCKPKG / "PRIMARY_ANALYSIS_LOCK.sha256").read_text().split()[0]
status = "VERIFIED" if lock_sha == expected else "FAILED"
(PKG / "00_LOCK_VERIFICATION.md").write_text(
    f"# Lock verification\n\n- file: PRIMARY_ANALYSIS_LOCK.yaml\n"
    f"- computed SHA-256: `{lock_sha}`\n- expected: `{expected}`\n\n"
    f"LOCK_STATUS: {status}\n")
if status != "VERIFIED":
    raise SystemExit("LOCK FAILED — aborting before beta3")

# ---- PHASE 1: exact sample ------------------------------------------------
S = pd.read_csv(LOCKPKG / "analysis" / "primary_sample_preoutcome.csv")
n_src = len(S)
req = S.dropna(subset=["hhi", "jsd", "mismatch"]).copy()
req = req[(req.subregion.notna()) & (req.subregion != "none")]
est = req.reset_index(drop=True)
assert len(est) == 147, f"N={len(est)} != 147 — ABORT"
est.to_csv(AN / "PRIMARY_ESTIMATION_SAMPLE_LOCKED.csv", index=False)
sam_sha = hashlib.sha256(
    (AN / "PRIMARY_ESTIMATION_SAMPLE_LOCKED.csv").read_bytes()).hexdigest()
(AN / "PRIMARY_ESTIMATION_SAMPLE_LOCKED.sha256").write_text(
    f"{sam_sha}  PRIMARY_ESTIMATION_SAMPLE_LOCKED.csv\n")
(PKG / "01_SAMPLE_VERIFICATION.md").write_text(
    f"# Sample verification\n\n- source N: {n_src}\n"
    f"- excluded, mismatch missing: {n_src - int(S.mismatch.notna().sum())}\n"
    f"- excluded, other required field: "
    f"{int(S.mismatch.notna().sum()) - len(est)}\n"
    f"- final N: {len(est)}\n"
    f"- M49 subregions: {est.subregion.nunique()}\n"
    f"- SHA-256: `{sam_sha}`\n")

# ---- PHASE 2: variables ----------------------------------------------------
MU = dict(hhi=est.hhi.mean(), mismatch=est.mismatch.mean())
SD = dict(hhi=est.hhi.std(), mismatch=est.mismatch.std())
y = (est.jsd / JSD_MAX).values
H = ((est.hhi - MU["hhi"]) / SD["hhi"]).values
M = ((est.mismatch - MU["mismatch"]) / SD["mismatch"]).values
X = np.column_stack([np.ones(len(est)), H, M, H * M])
meta = dict(means=MU, sds=SD, jsd_max=JSD_MAX)

# ---- PHASE 3: first opening ------------------------------------------------
fit = sm.GLM(y, X, family=sm.families.Binomial()).fit()
opening = dict(
    timestamp=datetime.now(timezone.utc).isoformat(),
    lock_sha256=lock_sha, sample_sha256=sam_sha, N=int(len(est)),
    beta0=float(fit.params[0]), beta1=float(fit.params[1]),
    beta2=float(fit.params[2]), beta3=float(fit.params[3]),
    converged=bool(fit.converged),
    deviance=float(fit.deviance), pearson_chi2=float(fit.pearson_chi2),
    llf=float(fit.llf), standardization=meta)
(AN / "PRIMARY_FIRST_OPENING.json").write_text(json.dumps(opening, indent=2))
open_sha = hashlib.sha256(
    (AN / "PRIMARY_FIRST_OPENING.json").read_bytes()).hexdigest()
(AN / "PRIMARY_FIRST_OPENING.sha256").write_text(
    f"{open_sha}  PRIMARY_FIRST_OPENING.json\n")
print("beta3 first opening:", opening["beta3"])

# ---- PHASE 4: subregion cluster bootstrap ----------------------------------
rng = np.random.default_rng(SEED)
sub = est.subregion.values
subs = np.unique(sub)
Hp25, Hp50, Hp75 = np.percentile(est.hhi, [25, 50, 75])
def z_h(h): return (h - MU["hhi"]) / SD["hhi"]

def effects(params):
    """ME of +1 SD mismatch in JSD units at HHI P25/50/75 + Delta."""
    b = params
    out = {}
    for tag, h in (("P25", Hp25), ("P50", Hp50), ("P75", Hp75)):
        hz = z_h(h)
        m0 = M  # at each country's own mismatch? -> discrete-1sd change:
        # contrast defined at given HHI across observed M support is a
        # conditional effect: ME = dE[y]/dM * 1SD evaluated at HHI level.
        # Use: E[y|M=m+1] - E[y|M=m] averaged over observed M at h_z.
        d = (1 / (1 + np.exp(-(b[0] + b[1] * hz + b[2] * (m0 + 1)
                               + b[3] * hz * (m0 + 1))))
             - 1 / (1 + np.exp(-(b[0] + b[1] * hz + b[2] * m0
                                 + b[3] * hz * m0))))
        out[tag] = float(d.mean() * JSD_MAX)
    out["Delta_ME"] = out["P75"] - out["P25"]
    return out

reps = []
for b_ in range(999):
    drawn = rng.choice(subs, size=len(subs), replace=True)
    idx = np.concatenate([np.flatnonzero(sub == g) for g in drawn])
    try:
        f = sm.GLM(y[idx], X[idx], family=sm.families.Binomial()
                   ).fit(disp=0, maxiter=50)
        e = effects(f.params)
        reps.append(dict(rep=b_, beta3=f.params[3],
                         ME_P25=e["P25"], ME_P50=e["P50"],
                         ME_P75=e["P75"], Delta_ME=e["Delta_ME"]))
    except Exception:
        reps.append(dict(rep=b_, beta3=np.nan, ME_P25=np.nan,
                         ME_P50=np.nan, ME_P75=np.nan, Delta_ME=np.nan))
reps = pd.DataFrame(reps)
reps.to_csv(AN / "primary_bootstrap_replicates.csv", index=False)
ok = reps.dropna()

def ci(col):
    v = np.sort(ok[col].values)
    return float(v[int(0.025 * len(v))]), float(v[int(0.975 * len(v)) - 1])

b3 = float(fit.params[3]); b3_ci = ci("beta3")
peff = effects(fit.params)
row = dict(beta0=fit.params[0], beta1=fit.params[1], beta2=fit.params[2],
           beta3=b3, beta3_ci_lo=b3_ci[0], beta3_ci_hi=b3_ci[1],
           valid_replicates=int(len(ok)), n=len(est),
           beta3_p_boot=float(2 * min((ok.beta3 <= 0).mean(),
                                      (ok.beta3 >= 0).mean())))
pd.DataFrame([row]).to_csv(AN / "primary_model_results.csv", index=False)

eff_rows = []
for k, lab in (("ME_P25", "P25"), ("ME_P50", "P50"), ("ME_P75", "P75"),
               ("Delta_ME", "Delta_ME")):
    lo, hi = ci(k)
    eff_rows.append(dict(effect=k, estimate=peff[lab], ci_lo=lo, ci_hi=hi,
                         scale="JSD"))
pd.DataFrame(eff_rows).to_csv(AN / "primary_effects.csv", index=False)
print(json.dumps({"beta3": b3, "ci": b3_ci,
                  "effects": {r["effect"]: [r["estimate"], r["ci_lo"], r["ci_hi"]]
                              for r in eff_rows}}, indent=1))
np.save(PKG / "_cache_y.npy", y); np.save(PKG / "_cache_X.npy", X)
est.to_parquet(PKG / "_cache_est.parquet")
json.dump(meta, open(PKG / "_cache_meta.json", "w"))
