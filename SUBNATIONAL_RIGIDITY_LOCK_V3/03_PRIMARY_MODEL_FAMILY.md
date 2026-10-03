# 03 Primary model family

Frozen model: **`jsd ~ irr_share_base2000 + mismatch_T +
irr_share_base2000:mismatch_T + C(country)`**, estimated by **OLS with
country fixed effects**, standard errors by 10°-grid block bootstrap
(B = 999, seed 20261003), two-sided α = 0.05.

## Candidates compared (never on b3)

| family | support | residual diagnostics | bootstrap compatibility | interpretability | verdict |
|---|---|---|---|---|---|
| **A. OLS + country FE** | JSD real-valued but generated contrast scale linear; estimates on JSD units | residual sd ~0.1, no unit bound violated in sims | fast lstsq; stable under block resampling (0 failures in 1,400 sim fits) | b3 in JSD units — directly readable | **PRIMARY** |
| B. fractional-logit GLM + country FE | (0,1) bounded — theoretically cleanest for JSD | link-scale coefficients need delta-method transforms | slower, occasional non-convergence risk under resampling | requires marginal-effect translation | robustness check |
| C. beta regression | (0,1) open support; JSD can attain 0/1 edge values | precision modelling adds parameters | heavy and fragile in bootstrap | least interpretable | rejected |

## Decision

Family A is frozen as primary: the interaction coefficient on the JSD
scale is the estimand the hypothesis statement uses, residuals behave
within the bounded support (observed JSD range 0.02–0.94, predicted mass
well inside), and the spatially-block-resampled SEs are calibrated
(type-I 3.5–6.5%; see 05). Family B is the prespecified robustness
alternative; family C rejected for stability.

Covariate protocol unchanged from v2: HHI is a mechanism-control model
only, log area a precision covariate only, perennial share a separate
secondary exposure — none enter the primary formula.
