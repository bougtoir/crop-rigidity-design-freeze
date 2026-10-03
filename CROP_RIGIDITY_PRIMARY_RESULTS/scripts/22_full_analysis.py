#!/usr/bin/env python3
"""22_full_analysis.py — figures, secondary inference, robustness,
falsification, exploratory subgroups. Runs AFTER PRIMARY_FIRST_OPENING.json.
Re-runs the identical frozen bootstrap to also store full param vectors
(needed for prediction/ME bands); replicate file is regenerated with the
extra columns — the lock and first-opening records are untouched.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from statsmodels.othermod.betareg import BetaModel

ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "CROP_RIGIDITY_PRIMARY_RESULTS"
AN = PKG / "analysis"; FIG = PKG / "figures"
LOCK = ROOT / "CROP_RIGIDITY_FINAL_LOCK"
REPAIR = ROOT / "CROP_RIGIDITY_PREANALYSIS_REPAIR"
RAW = ROOT / "data" / "raw"
JSD_MAX = float(np.sqrt(np.log(2)))
SEED = 20261003
rng = np.random.default_rng(SEED)

est = pd.read_parquet(PKG / "_cache_est.parquet")
y = np.load(PKG / "_cache_y.npy"); X = np.load(PKG / "_cache_X.npy")
meta = json.load(open(PKG / "_cache_meta.json"))
MU, SDv = meta["means"], meta["sds"]
H, M = X[:, 1], X[:, 2]
sub = est.subregion.values
subs = np.unique(sub)
fit = sm.GLM(y, X, family=sm.families.Binomial()).fit()
Hp25, Hp50, Hp75 = np.percentile(est.hhi, [25, 50, 75])

def z_h(h): return (h - MU["hhi"]) / SDv["hhi"]
def z_m(m): return (m - MU["mismatch"]) / SDv["mismatch"]
def sig(z): return 1 / (1 + np.exp(-z))

def me_at(b, hz):
    mz = z_m(est.mismatch.values)
    return float((sig(b[0] + b[1] * hz + b[2] * (mz + 1) + b[3] * hz * (mz + 1))
                  - sig(b[0] + b[1] * hz + b[2] * mz + b[3] * hz * mz)).mean()
                 * JSD_MAX)

# frozen bootstrap with full params (identical resampling scheme)
reps = []
for b_ in range(999):
    drawn = rng.choice(subs, size=len(subs), replace=True)
    idx = np.concatenate([np.flatnonzero(sub == g) for g in drawn])
    try:
        f = sm.GLM(y[idx], X[idx], family=sm.families.Binomial()
                   ).fit(disp=0, maxiter=50)
        b = f.params
        reps.append(dict(rep=b_, beta0=b[0], beta1=b[1], beta2=b[2],
                         beta3=b[3], ME_P25=me_at(b, z_h(Hp25)),
                         ME_P50=me_at(b, z_h(Hp50)),
                         ME_P75=me_at(b, z_h(Hp75)),
                         Delta_ME=me_at(b, z_h(Hp75)) - me_at(b, z_h(Hp25))))
    except Exception:
        reps.append(dict(rep=b_, beta0=np.nan, beta1=np.nan, beta2=np.nan,
                         beta3=np.nan, ME_P25=np.nan, ME_P50=np.nan,
                         ME_P75=np.nan, Delta_ME=np.nan))
reps = pd.DataFrame(reps)
reps.to_csv(AN / "primary_bootstrap_replicates.csv", index=False)
ok = reps.dropna()
P = ok[["beta0", "beta1", "beta2", "beta3"]].values

# ---------------- figures ---------------------------------------------------
hhi_t = pd.qcut(est.hhi, 3, labels=["low", "mid", "high"])
fig, ax = plt.subplots(figsize=(7, 5))
for t, c in zip(["low", "mid", "high"], ["#1f77b4", "#2ca02c", "#d62728"]):
    m_ = (hhi_t == t).values
    ax.scatter(est.mismatch[m_], est.jsd[m_], s=18, alpha=0.7, label=f"HHI {t}")
ax.set_xlabel("Dominant-crop crop-calendar climatic mismatch (Mahalanobis)")
ax.set_ylabel("Crop-mix transformation (JSD)")
ax.legend(title="Specialization")
fig.tight_layout(); fig.savefig(FIG / "primary_scatter.png", dpi=200); plt.close(fig)

mz_g = np.linspace(z_m(est.mismatch.min()), z_m(est.mismatch.max()), 120)
fig, ax = plt.subplots(figsize=(7, 5))
for h, lab, c in [(Hp25, "P25", "#1f77b4"), (Hp50, "P50", "#2ca02c"),
                  (Hp75, "P75", "#d62728")]:
    hz = z_h(h)
    pr = sig(fit.params[0] + fit.params[1] * hz + fit.params[2] * mz_g
             + fit.params[3] * hz * mz_g) * JSD_MAX
    boot = np.array([sig(bb[0] + bb[1] * hz + bb[2] * mz_g
                         + bb[3] * hz * mz_g) * JSD_MAX for bb in P])
    lo, hi = np.percentile(boot, [2.5, 97.5], axis=0)
    ax.plot(z_m(mz_g) * 0 + (mz_g * SDv["mismatch"] + MU["mismatch"]), pr,
            color=c, label=f"HHI {lab}")
    ax.fill_between(mz_g * SDv["mismatch"] + MU["mismatch"], lo, hi,
                    color=c, alpha=0.12)
ax.set_xlabel("Dominant-crop climatic mismatch"); ax.set_ylabel("Expected JSD")
ax.legend(title="HHI percentile")
fig.tight_layout(); fig.savefig(FIG / "primary_predictions.png", dpi=200)
plt.close(fig)

hz_g = np.linspace(z_h(est.hhi.min()), z_h(est.hhi.max()), 120)
me_curve = np.array([me_at(fit.params, h) for h in hz_g])
boot_me = np.array([[me_at(b, h) for h in hz_g] for b in P])
band = np.percentile(boot_me, [2.5, 97.5], axis=0).T
fig, ax = plt.subplots(figsize=(7, 5))
xs = hz_g * SDv["hhi"] + MU["hhi"]
ax.plot(xs, me_curve, color="k")
ax.fill_between(xs, band[:, 0], band[:, 1], alpha=0.2, color="k")
ax.axhline(0, ls="--", lw=0.8, color="gray")
ax.set_xlabel("Legacy specialization (HHI)")
ax.set_ylabel("Marginal effect of +1 SD mismatch (JSD)")
fig.tight_layout(); fig.savefig(FIG / "marginal_effect_curve.png", dpi=200)
plt.close(fig)

eff = pd.read_csv(AN / "primary_effects.csv")
fig, ax = plt.subplots(figsize=(6, 4))
ypos = np.arange(len(eff))[::-1]
ax.errorbar(eff.estimate, ypos,
            xerr=[eff.estimate - eff.ci_lo, eff.ci_hi - eff.estimate],
            fmt="o", color="k", capsize=4)
ax.axvline(0, ls="--", lw=0.8, color="gray")
ax.set_yticks(ypos); ax.set_yticklabels(eff.effect)
ax.set_xlabel("Change in JSD (95% CI)")
fig.tight_layout(); fig.savefig(FIG / "primary_effect_forest.png", dpi=200)
plt.close(fig)
print("figures done")

# ---------------- secondary inference --------------------------------------
tile = ((np.floor(est.centroid_lon / 30) * 100
         + np.floor(est.centroid_lat / 30)).astype(int)).values
tiles = np.unique(tile)
bb = []
for b_ in range(999):
    drawn = rng.choice(tiles, size=len(tiles), replace=True)
    idx = np.concatenate([np.flatnonzero(tile == g) for g in drawn])
    try:
        f = sm.GLM(y[idx], X[idx], family=sm.families.Binomial()
                   ).fit(disp=0, maxiter=50)
        bb.append(f.params[3])
    except Exception:
        continue
bb = np.sort(bb)
bb_ci = (float(bb[int(0.025 * len(bb))]), float(bb[int(0.975 * len(bb)) - 1]))
hc2 = float(fit.bse[3])
secondary = dict(beta3=float(fit.params[3]),
                 blockboot_ci=list(bb_ci), blockboot_B=int(len(bb)),
                 hc2_ci=[float(fit.params[3] - 1.96 * hc2),
                         float(fit.params[3] + 1.96 * hc2)])
json.dump(secondary, open(AN / "secondary_inference.json", "w"), indent=2)
print("secondary:", secondary)
