# 06 Information assessment (v3)

`scripts/information_simulation_v3.py` → `analysis/information_simulation_v3.csv`.
Fully outcome-blind: the DGP uses only marginal moments (baseline mean
μ = 0.13, noise SD = 0.09 on the JSD support), a fresh country effect per
replicate, and spatially correlated noise (rho = 500 km). The observed
unit-level JSD vector is never read.

## DGP

```
Y_i = μ + g_country(i) + 0.10·z_irr − 0.05·z_mm + b3·z_int + e_spatial,i
```

Predictors are standardized observed exposures (allowed — exposures
define the estimand, they are not the outcome). Because E[Y|X] = Xβ
exactly, the population OLS coefficient on z_int equals b3; under
b3 = 0 the induced interaction is **1.27e-16 < 1e-8** (exact null).

## Results (200 reps/scenario, grid10 block bootstrap)

| true b3 | label | induced contrast (JSD) | bias | RMSE | coverage | type-I / power | median CI width |
|---|---|---|---|---|---|---|---|
| 0.00 | null | 0.0000 | −0.0004 | 0.0045 | 0.975 | type-I 0.025 | 0.022 |
| +0.15 | small | +0.0153 | 0.0000 | 0.0049 | 0.965 | power 1.0 | 0.022 |
| +0.30 | moderate | +0.0306 | −0.0004 | 0.0046 | 0.975 | 1.0 | 0.023 |
| +0.50 | large | +0.0509 | +0.0001 | 0.0051 | 0.970 | 1.0 | 0.022 |
| −0.15 | small− | −0.0153 | −0.0000 | 0.0047 | 0.985 | 1.0 | 0.023 |
| −0.30 | moderate− | −0.0306 | +0.0003 | 0.0044 | 0.970 | 1.0 | 0.021 |
| −0.50 | large− | −0.0509 | +0.0004 | 0.0044 | 0.975 | 1.0 | 0.024 |

## Reading

* Estimator is unbiased (|bias| ≤ 4e-4) and CI coverage 96.5–98.5%.
* Power = 1.0 for |b3| ≥ 0.15 SD-units — the design detects even small
  interactions on either sign; a null result would be informative
  (CI half-width ≈ 0.011 on the standardized interaction scale).
* Reproducibility: the script emits this CSV deterministically;
  `scripts/package_validation.py` re-runs it and verifies
  byte-identical output plus the <1e-8 exact-null assertion.
