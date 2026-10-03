#!/usr/bin/env python3
"""H4 Kitagawa (Oaxaca-type) exact decomposition — SECONDARY.

For each crop k and country, over each unit's locked baseline/endline
years:

  Delta_k = W_k + B_k + I_k
  W_k = within-unit crop-share change (baseline area weights)
  B_k = geographic redistribution of total agricultural area
  I_k = interaction of the two

Signed components and absolute contributions reported; B alone is
never labelled 'adaptation escape'. Uses the locked sample's units and
the admin_crop_observation_matrix.
"""
import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from pipeline_common import ANA, FIG, ROOT, verify_lock, load_sample

verify_lock()
dm = load_sample()
obs = pd.read_parquet(ROOT / "SUBNATIONAL_RIGIDITY_DESIGN_FREEZE"
                      / "analysis" / "admin_crop_observation_matrix.parquet")

rows = []
for (c, iso), g0 in dm.groupby(["country", "country"]):
    pass

# per unit: baseline year y0, endline y1 from locked sample
for _, u in dm.iterrows():
    sub = obs[(obs.unit_id == u.unit_id)
              & (obs.year.isin([int(u.y0), int(u.y1)]))]
    if sub.year.nunique() < 2:
        continue
    pv = sub.pivot_table(index="crop", columns="year", values="area_ha",
                         aggfunc="sum").fillna(0)
    y0c, y1c = int(u.y0), int(u.y1)
    tot0, tot1 = pv[y0c].sum(), pv[y1c].sum()
    if tot0 <= 0 or tot1 <= 0:
        continue
    for crop in pv.index:
        s0, s1 = pv.loc[crop, y0c] / tot0, pv.loc[crop, y1c] / tot1
        rows.append(dict(country=u.country, unit_id=u.unit_id, crop=crop,
                         share0=s0, share1=s1, area0=tot0, area1=tot1))
su = pd.DataFrame(rows)

# Kitagawa per country x crop:
# Delta_k = (sum_u A1u*s1u - sum_u A0u*s0u)/A_tot1_national? Use
# national-level decomposition: national share change of crop k
#   = sum_u (w1u s1u) - sum_u (w0u s0u), w = unit area share in country
# W_k = sum_u w0u (s1u - s0u)        (within, baseline weights)
# B_k = sum_u (w1u - w0u) s0u        (between/redistribution)
# I_k = sum_u (w1u - w0u)(s1u - s0u) (interaction)
out = []
for (c, crop), g in su.groupby(["country", "crop"]):
    a0, a1 = g.area0.values, g.area1.values
    w0 = a0 / a0.sum()
    w1 = a1 / a1.sum()
    s0, s1 = g.share0.values, g.share1.values
    d_national = float((w1 * s1).sum() - (w0 * s0).sum())
    W = float((w0 * (s1 - s0)).sum())
    B = float(((w1 - w0) * s0).sum())
    I = float(((w1 - w0) * (s1 - s0)).sum())
    err = abs(d_national - (W + B + I))
    out.append(dict(country=c, crop=crop, delta_share=d_national,
                    W=W, B=B, I=I, exact_err=err,
                    abs_W=abs(W), abs_B=abs(B), abs_I=abs(I)))
h4 = pd.DataFrame(out)
h4.to_csv(ANA / "H4_decomposition_results.csv", index=False)
summ = h4.groupby("country")[["abs_W", "abs_B", "abs_I"]].sum()
summ["share_B"] = summ.abs_B / summ.sum(axis=1)
print("max decomposition error:", h4.exact_err.max())
print(summ.round(3).to_string())

# figure: stacked signed/abs contributions per country
fig, ax = plt.subplots(figsize=(7.5, 4.2))
cs = summ.index
x = np.arange(len(cs))
ax.bar(x, summ.abs_W, label="|W| within-unit")
ax.bar(x, summ.abs_B, bottom=summ.abs_W, label="|B| redistribution")
ax.bar(x, summ.abs_I, bottom=summ.abs_W + summ.abs_B,
       label="|I| interaction")
ax.set_xticks(x, [c[:12] for c in cs], rotation=90, fontsize=6)
ax.set_ylabel("absolute share change (summed over crops)")
ax.legend(frameon=False, fontsize=8)
fig.tight_layout()
fig.savefig(FIG / "H4_decomposition.png")
plt.close(fig)
print("done")
