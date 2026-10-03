# 02 — Primary result

Primary hypothesis (frozen): legacy specialization (HHI, 1981–2001) conditions the
effect of climatic mismatch (dominant-crop MIRCA2000 crop-calendar Mahalanobis
displacement, 2002–2020 vs 1984–2001) on crop-mix transformation (JSD,
1981–2001 → 2002–2020).

Model (frozen): fractional logit, `logit(E[y]) = β0 + β1·HHI_z + β2·M_z + β3·HHI_z·M_z`,
`y = JSD / √ln 2`, all predictors standardized with locked-sample moments
(HHI mean 0.2343, SD 0.1353; mismatch mean 0.5609, SD 0.4249). N = 147.

## First opening (recorded before any other specification)

| Parameter | Estimate |
|---|---|
| β0 | −1.3670 |
| β1 (HHI) | −0.1018 |
| β2 (mismatch) | −0.0112 |
| **β3 (HHI × mismatch)** | **+0.00459** |

- Inference (frozen): M49-subregion cluster bootstrap, B = 999, seed 20261003,
  two-sided percentile 95% CI. Valid replicates: 999/999.
- **β3 = +0.0046, 95% CI [−0.131, +0.143]**.
- The bootstrap p-value (two-sided, percentile) is ≈ 1.0 — the CI is centered
  almost exactly on zero and the point estimate is ~3% of a standardized-unit
  effect.
- `analysis/PRIMARY_FIRST_OPENING.json` (+`.sha256`) was written immediately
  after the first fit, before any other model was run.

## Secondary inference (post-opening, pre-registered diagnostic layer)

| Method | β3 95% CI |
|---|---|
| 30°×30° tile block bootstrap (B=999) | [−0.186, +0.105] |
| HC2 (diagnostic only) | [−0.422, +0.431] |

Both secondary methods agree with the primary inference: the interaction is
statistically indistinguishable from zero.

## Interpretation under the frozen three-way rule

The estimate is closest to the frozen "β3 ≈ 0" outcome: a tight, informative
null. The design detects |β3| ≥ 0.3 SD with power ≈ 1.0 (power v3), so the
CI's width (~0.27 SD-units) rules out anything beyond a weak conditioning
effect in either direction. No claim of causation is made; this is an
observational interaction estimate.
