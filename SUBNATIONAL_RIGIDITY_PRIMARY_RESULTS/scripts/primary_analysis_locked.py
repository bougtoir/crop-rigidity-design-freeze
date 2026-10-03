#!/usr/bin/env python3
"""FIRST AND ONLY real primary opening — locked V4 subnational model.

Verifies lock + sample SHA-256 (ABORT on mismatch), fits
  jsd ~ irr_share_base2000 + mismatch_T + irr:mismatch + C(country)
exactly once on the frozen 340-unit sample (original scales), writes the
immutable PRIMARY_FIRST_OPENING_SUBNATIONAL.json + sha256, then runs the
frozen grid10 block bootstrap (B=999, seed 20261003) and the locked
interpretable effects (Delta_ME, ME at I P25/P50/P75). Figures 1-4.
"""
import json, sys
from datetime import datetime, timezone
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, str(__file__ and __import__('pathlib').Path(__file__).parent))
from pipeline_common import (RES, ANA, FIG, SEED, V3, V4,
                             verify_lock, load_sample, design, ols,
                             block_boot_est, sha256)

s_sha, l_sha = verify_lock()
print("LOCK_STATUS: VERIFIED", s_sha[:16], l_sha[:16])

dm = load_sample()
N = len(dm)
X, names = design(dm)
y = dm.jsd.values
b, resid = ols(X, y)
i_irr, i_mm, i_int = 1, 2, 3

rec = dict(
    timestamp_utc=datetime.now(timezone.utc).isoformat(),
    lock_sha256=l_sha, sample_sha256=s_sha,
    N=N, countries=int(dm.country.nunique()),
    model="jsd ~ irr_share_base2000 + mismatch_T + irr:mm + C(country) [OLS]",
    beta0=float(b[0]), beta1_irr=float(b[i_irr]), beta2_mm=float(b[i_mm]),
    beta3_interaction=float(b[i_int]),
    r2=float(1 - (resid ** 2).sum() / ((y - y.mean()) ** 2).sum()),
    resid_sd=float(resid.std(ddof=X.shape[1])),
    rank=int(np.linalg.matrix_rank(X)),
)
ANA.mkdir(parents=True, exist_ok=True)
fp = ANA / "PRIMARY_FIRST_OPENING_SUBNATIONAL.json"
fp.write_text(json.dumps(rec, indent=2))
(ANA / "PRIMARY_FIRST_OPENING_SUBNATIONAL.sha256").write_text(
    f"{sha256(fp)}  PRIMARY_FIRST_OPENING_SUBNATIONAL.json\n")
print("FIRST OPENING:", {k: round(v, 6) for k, v in rec.items() if isinstance(v, float)})

# ---- frozen bootstrap: grid10, B=999 ----
boot = block_boot_est(dm, X, y, "block_grid10", B=999, seed=SEED)
bd = pd.DataFrame(boot[:, :4], columns=["const", "irr", "mm", "irr_x_mm"])
bd.to_csv(ANA / "primary_block_bootstrap_999.csv", index=False)
b3s = bd.irr_x_mm.values
lo, hi = np.quantile(b3s, [0.025, 0.975])
p_two = float(2 * min((b3s <= 0).mean(), (b3s >= 0).mean()))

# ---- interpretable effects (original JSD scale) ----
I = dm.irr_share_base2000.values
M = dm.mismatch_T.values
I25, I50, I75 = np.quantile(I, [0.25, 0.5, 0.75])
sdM = M.std(ddof=1)
Delta_ME = b[i_int] * (I75 - I25) * sdM
me_pts = {}
for lab, iv in [("P25", I25), ("P50", I50), ("P75", I75)]:
    me_pts[lab] = (b[i_mm] + b[i_int] * iv) * sdM
# bootstrap CIs for effects
bI = bd.irr.values; bM = bd.mm.values; bX = bd.irr_x_mm.values
dme_s = bX * (I75 - I25) * sdM
me_s = {lab: (bM + bX * iv) * sdM for lab, iv in
        [("P25", I25), ("P50", I50), ("P75", I75)]}

eff = pd.DataFrame([
    dict(effect="Delta_ME", point=Delta_ME,
         ci_lo=np.quantile(dme_s, .025), ci_hi=np.quantile(dme_s, .975)),
    *[dict(effect=f"ME_{k}", point=me_pts[k],
           ci_lo=np.quantile(v, .025), ci_hi=np.quantile(v, .975))
      for k, v in me_s.items()],
    dict(effect="beta3", point=b[i_int], ci_lo=lo, ci_hi=hi),
    dict(effect="beta1_irr", point=b[i_irr],
         ci_lo=np.quantile(bI, .025), ci_hi=np.quantile(bI, .975)),
    dict(effect="beta2_mm", point=b[i_mm],
         ci_lo=np.quantile(bM, .025), ci_hi=np.quantile(bM, .975)),
])
eff.to_csv(ANA / "primary_effects.csv", index=False)

pd.DataFrame([dict(
    N=N, countries=dm.country.nunique(),
    beta1=b[i_irr], beta2=b[i_mm], beta3=b[i_int],
    beta3_ci_lo=lo, beta3_ci_hi=hi, beta3_p_two_sided=p_two,
    bootstrap="grid10", B=int(len(b3s)), seed=SEED, alpha=0.05,
    r2=rec["r2"], Delta_ME=Delta_ME,
    Delta_ME_ci_lo=float(np.quantile(dme_s, .025)),
    Delta_ME_ci_hi=float(np.quantile(dme_s, .975)),
)]).to_csv(ANA / "primary_model_results.csv", index=False)

print(f"b3={b[i_int]:.4f} [{lo:.4f},{hi:.4f}] p={p_two:.4f} "
      f"Delta_ME={Delta_ME:.4f}")

# ---- Figures ----
FIG.mkdir(parents=True, exist_ok=True)
plt.rcParams.update({"figure.dpi": 150, "font.size": 9})

# Fig 1: observed jsd vs mismatch, irrigation terciles
terc = pd.qcut(dm.irr_share_base2000, 3, labels=["low", "mid", "high"])
fig, ax = plt.subplots(figsize=(5.2, 3.6))
for lab, c in zip(["low", "mid", "high"], ["#1f77b4", "#7f7f7f", "#d62728"]):
    m = terc == lab
    ax.scatter(dm.mismatch_T[m], dm.jsd[m], s=14, alpha=.65, c=c,
               label=f"irrigation tercile: {lab}")
ax.set_xlabel("climatic mismatch (deg C, calendar-weighted)")
ax.set_ylabel("JSD (crop-mix transformation)")
ax.legend(frameon=False, fontsize=8)
fig.tight_layout(); fig.savefig(FIG / "primary_scatter.png"); plt.close(fig)

# Fig 2: predicted mismatch-JSD at I P25/P50/P75
grid_m = np.linspace(M.min(), M.max(), 100)
fig, ax = plt.subplots(figsize=(5.2, 3.6))
for iv, lab, c in [(I25, "P25", "#1f77b4"), (I50, "P50", "#7f7f7f"),
                   (I75, "P75", "#d62728")]:
    fe_adj = (b[0] + np.mean([b[4 + j] for j in range(fe_n)])
              if (fe_n := X.shape[1] - 4) else b[0])
    ax.plot(grid_m, fe_adj + b[1] * iv + b[2] * grid_m
            + b[3] * iv * grid_m, c=c,
            label=f"irrigation {lab} = {iv:.3f}")
ax.scatter(M, y, s=8, alpha=.15, c="k")
ax.set_xlabel("climatic mismatch (deg C)"); ax.set_ylabel("predicted JSD")
ax.legend(frameon=False, fontsize=8)
fig.tight_layout(); fig.savefig(FIG / "primary_predictions.png"); plt.close(fig)

# Fig 3: marginal effect of +1sd mismatch over irrigation support
ig = np.linspace(I.min(), I.max(), 200)
me_curve = (b[i_mm] + b[i_int] * ig) * sdM
me_lo = np.quantile((bM[:, None] + bX[:, None] * ig) * sdM, .025, axis=0)
me_hi = np.quantile((bM[:, None] + bX[:, None] * ig) * sdM, .975, axis=0)
fig, ax = plt.subplots(figsize=(5.2, 3.6))
ax.fill_between(ig, me_lo, me_hi, alpha=.25, color="#1f77b4")
ax.plot(ig, me_curve, c="#1f77b4")
ax.axhline(0, c="k", lw=.6, ls="--")
ax.hist(I, bins=30, weights=np.full(N, (me_hi.max() - me_lo.min()) / N * 3),
        bottom=me_lo.min(), alpha=.15, color="gray")
ax.set_xlabel("baseline irrigation share (SPAM2000)")
ax.set_ylabel("ME of +1 SD mismatch (JSD)")
fig.tight_layout(); fig.savefig(FIG / "marginal_effect_curve.png"); plt.close(fig)

# Fig 4: forest of ME_P25/50/75 + Delta_ME
fig, ax = plt.subplots(figsize=(5.2, 3.2))
labs = ["Delta_ME", "ME_P25", "ME_P50", "ME_P75"]
pts = [Delta_ME] + [me_pts[k] for k in ["P25", "P50", "P75"]]
los = [np.quantile(dme_s, .025)] + [np.quantile(me_s[k], .025) for k in ["P25", "P50", "P75"]]
his = [np.quantile(dme_s, .975)] + [np.quantile(me_s[k], .975) for k in ["P25", "P50", "P75"]]
for i, (p, l_, h_) in enumerate(zip(pts, los, his)):
    ax.errorbar(p, i, xerr=[[p - l_], [h_ - p]], fmt="o", c="#1f77b4", capsize=3)
ax.axvline(0, c="k", lw=.6, ls="--")
ax.set_yticks(range(4), labs); ax.invert_yaxis()
ax.set_xlabel("effect on original JSD scale")
fig.tight_layout(); fig.savefig(FIG / "primary_effect_forest.png"); plt.close(fig)
print("done")
