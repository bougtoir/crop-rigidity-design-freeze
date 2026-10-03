# 05 — Primary estimand

## Model (primary, frozen)

    TRANSFORM_i = β0 + β1·Mismatch_i + β2·Legacy_i + β3·(Mismatch_i × Legacy_i)
                  + γ·X_i + FE_region + ε_i

- TRANSFORM_i = Jensen–Shannon crop-mix distance (continuous, bounded).
- Mismatch_i = Mahalanobis climate displacement for the legacy dominant crop
  (03_ENVIRONMENTAL_MISMATCH_PROTOCOL.md).
- Legacy_i = HHI on 1981–2000 harvested-area shares (primary dimension A).
- X_i = frozen confounder set (06_COVARIATE_TABLE.csv).
- Estimator: fractional logit (outcome bounded in (0,1)) with HC2 robust SEs;
  OLS reported alongside as a transparent sensitivity spec. Inference
  additionally by region-clustered bootstrap (regions = UN macro regions).

## Primary target: β3

Coding direction: **higher HHI = more specialized**; **higher JSD = more
transformation**.

## Pre-specified interpretation of β3 (all three admissible)

| Result | Interpretation |
|---|---|
| β3 < 0 | specialization suppresses transformation under climatic mismatch — consistent with the rigidity hypothesis |
| β3 ≈ 0 | pre-existing specialization does not condition the transformation response — null is a publishable answer |
| β3 > 0 | specialized systems transform *more* under mismatch (e.g. forced restructuring when a monoculture niche collapses) — scientifically important, NOT an analysis failure |

The sign is reported as estimated; no re-coding or metric-swapping is
permitted to make β3 conform to the rigidity direction.

## Estimand statement

β3 estimates the average modification, per unit legacy concentration, of the
slope relating climatic mismatch to observed crop-mix transformation across
countries, conditional on X_i. It is associational-causal: the identification
claims rest on (a) temporal ordering (legacy strictly precedes exposure and
outcome windows), (b) exclusion of outcome-window information from all
predictors, and (c) the frozen falsification battery (08).
