# 04 Information assessment (v4, bounded DGP)

`analysis/information_simulation_v4.csv` — 200 replicates per contrast,
grid10 block bootstrap, OLS + country FE. JSD-scale contrast = change in
the +1SD-mismatch effect between irrigation-P75 and P25 units;
latent b3 solved to match each target contrast.

| JSD target | latent b3 | induced JSD interaction | bias | rmse | coverage | power / type-I |
|---|---|---|---|---|---|---|
| 0.00 | 0.000 | −0.0041 | +0.001 | 0.012 | 0.955 | type-I 0.050 |
| +0.01 | −0.592 | −0.0719 | +0.015 | 0.017 | 0.995 | 0.780 |
| +0.02 | −0.708 | −0.0779 | +0.014 | 0.017 | 0.995 | 0.745 |
| +0.04 | −0.924 | −0.0872 | +0.014 | 0.016 | 1.000 | 0.570 |
| −0.01 | −0.324 | −0.0542 | +0.013 | 0.015 | 0.915 | 0.860 |
| −0.02 | +0.368 | +0.0403 | +0.009 | 0.012 | 1.000 | 0.980 |
| −0.04 | +0.758 | +0.0638 | +0.009 | 0.012 | 1.000 | 0.835 |

Notes:

* Exact latent null (0.0); induced JSD-scale null projection −0.0046 —
  OLS under the true null rejects at 5.0% (PASS) and covers 95.5%.
* OLS under bounded nonlinear DGP: bias ≤ 0.015 vs the induced target,
  coverage ≥ 91.5% — the frozen estimator remains acceptable → OLS
  retained (no redesign).
* Contrast→latent-b3 mapping is non-monotone on the positive side
  (saturation near the support edge); both scales are reported so the
  opening can read effects in JSD units directly.
* Power is asymmetric across the bounded grid (0.57–0.98); symmetric
  linear-grid power claims from v3 do not carry over — disclosed.
