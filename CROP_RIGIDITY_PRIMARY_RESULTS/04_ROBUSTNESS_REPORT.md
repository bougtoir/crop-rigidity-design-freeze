# 04 — Robustness report

All rows use the pre-registered estimator family; β3 (or the analogous
interaction) with 95% CI. Fractional-logit rows use the same subregion
cluster bootstrap (B=999, seed 20261003); alternative-family rows report
model-SE CIs (diagnostic).

| Spec | N | Exposure | Outcome / window | β3 [95% CI] |
|---|---|---|---|---|
| Primary (frozen) | 147 | dominant calendar mismatch | JSD | +0.005 [−0.131, +0.143] |
| A. Old ladder (legacy 81–00, expo 01–20) | 129 | dominant calendar mismatch | JSD | +0.000 [−0.176, +0.147] |
| B. Lagged (legacy 81–00, expo 01–10, out 11–20) | 129 | dominant calendar mismatch | JSD | +0.056 [−0.084, +0.155] |
| C. Thermal-season displacement | 148 | thermal-season mismatch | JSD | +0.019 [−0.063, +0.144] |
| D. Portfolio mismatch, coverage ≥0.70 | 130 | portfolio calendar mismatch | JSD | +0.009 [−0.116, +0.179] |
| D. Portfolio, coverage ≥0.50 | 151 | portfolio calendar mismatch | JSD | +0.007 [−0.115, +0.173] |
| D. Portfolio, coverage ≥0.80 | 100 | portfolio calendar mismatch | JSD | +0.032 [−0.132, +0.250] |
| E. Beta regression | 147 | dominant calendar mismatch | JSD | +0.020 [−0.047, +0.087] |
| E. OLS on logit(JSD) | 147 | dominant calendar mismatch | logit JSD | +0.024 [−0.045, +0.092] |
| F. Outcome = ΔHHI (exploratory) | 147 | dominant calendar mismatch | ΔHHI | +0.002 [−0.007, +0.010] |

## Reading

- Every pre-registered variant reproduces a small, statistically null
  interaction. No specification yields a negative (attenuating) β3; point
  estimates cluster between 0.00 and +0.06 SD-units.
- The largest point estimate (B_lagged, +0.056) still has a CI covering 0
  and its window swaps in a smaller lagged sample — it is not evidence of
  effect, and per protocol it is not used to reinterpret the primary null.
- E-family and F-family agree: model family and outcome scale do not change
  the conclusion.
- Nothing in the ledger upgrades or rescues the primary result; nothing
  contradicts it either. Consistent verdict: weak-to-null conditioning.

Source: `analysis/robustness_specification_ledger.csv`.
