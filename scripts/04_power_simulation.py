#!/usr/bin/env python3
"""04_power_simulation.py — simulation-based precision/power for beta3.

Uses the *measured* joint distribution of legacy HHI (from
analysis/design_diagnostics_summary.csv) and a realistic mismatch distribution,
simulates outcomes under small/moderate/large interaction effects, fits the
primary fractional-logit spec, and reports empirical CI width and power.

No effect sizes are taken from the previous noisy pilot.
"""
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.stats import norm
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
d = pd.read_csv(ROOT / "analysis" / "design_diagnostics_summary.csv")

rng = np.random.default_rng(20261003)
N = len(d)                      # 210 countries
hhi = d["hhi"].values
hhi_z = (hhi - hhi.mean()) / hhi.std()

NSIM = 400
results = []
# mismatch: standard normal with modest skew (many low-mismatch countries)
for label, b3 in [("zero", 0.0), ("small", -0.10), ("moderate", -0.25), ("large", -0.45)]:
    ests, los, his, ps = [], [], [], []
    for _ in range(NSIM):
        M = rng.standard_normal(N) + 0.4 * rng.standard_normal(N) ** 2 / np.sqrt(2)
        M = (M - M.mean()) / M.std()
        X = rng.standard_normal(N)
        eta = 0.05 * M + 0.05 * hhi_z + b3 * M * hhi_z + 0.05 * X
        mu = 1 / (1 + np.exp(-eta * 3))  # bounded outcome in (0,1)
        y = np.clip(mu + rng.normal(0, 0.08, N), 0.01, 0.99) * 0.6  # ~JSD scale
        Xd = sm.add_constant(np.column_stack([M, hhi_z, M * hhi_z, X]))
        try:
            m = sm.GLM(y, Xd, family=sm.families.Binomial()).fit(cov_type="HC2")
            ests.append(m.params[3]); ps.append(m.pvalues[3])
            ci = m.conf_int()[3]; los.append(ci[0]); his.append(ci[1])
        except Exception:
            continue
    ests = np.array(ests); ps = np.array(ps); his = np.array(his); los = np.array(los)
    results.append(dict(
        scenario=label, beta3_true=b3, nsim=len(ests),
        est_mean=ests.mean(), est_sd=ests.std(),
        ci_width_median=np.median(his - los),
        power_5pct=(ps < 0.05).mean(),
    ))
out = pd.DataFrame(results)
out.to_csv(ROOT / "analysis" / "power_simulation.csv", index=False)
print(out.to_string(index=False))

# spatial effective-N note: cluster sizes under region-clustering (5-8 macro regions)
print(f"N={N} countries; clustering at ~7 UN macro regions bounds effective"
      " independent units at << 210; reported CIs must use region bootstrap.")
