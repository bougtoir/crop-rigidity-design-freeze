# 01 Primary first opening (immutable record)

First and only fit of the frozen model on the locked V4 sample
(N = 340 units, 23 countries), OLS with country fixed effects,
original scales:

`jsd ~ irr_share_base2000 + mismatch_T + irr_share_base2000:mismatch_T + C(country)`

| coefficient | estimate |
|---|---|
| β0 (const) | +0.3395 |
| β1 irrigation | +0.0166 |
| β2 mismatch | −0.0062 |
| **β3 irrigation × mismatch** | **−0.0377** |
| R² | 0.604 |
| residual SD | 0.113 |

Immutable record: `analysis/PRIMARY_FIRST_OPENING_SUBNATIONAL.json`
(+ `.sha256`). Written before any robustness model was run.
