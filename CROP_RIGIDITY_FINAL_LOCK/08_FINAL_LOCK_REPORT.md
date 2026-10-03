# 08 — Final lock report

## Power v3 (`analysis/power_simulation_v3.csv`)

Continuous bounded JSD, fractional-logit family, two-sided 95% CI via
subregion cluster bootstrap, spatially correlated latent noise
(moderate scenario: `exp(-d/1500km)`), N=147 primary sample,
200 simulations per β3.

| β3 (standardized) | reject rate | median CI width | coverage |
|---|---|---|---|
| −1.0 | 1.000 | 0.197 | 0.920 |
| −0.6 | 1.000 | 0.190 | 0.960 |
| −0.3 | 1.000 | 0.162 | 0.945 |
| 0.0 | 0.055 | 0.150 | 0.990 |
| +0.3 | 0.995 | 0.152 | 0.985 |
| +0.6 | 1.000 | 0.169 | 0.950 |
| +1.0 | 1.000 | 0.210 | 0.885 |

The design is well powered for interactions of |β3| ≥ ~0.3 SD under the
validated error structure, symmetric in both directions, and the null
rejection rate is calibrated (~5.5%). Precision is reported
(CI width); a null result is informative, not merely underpowered.

## What changed vs the previous (premature) declaration

1. Power now runs on the frozen primary exposure+sample (dominant
   calendar mismatch, N=147), not the portfolio file.
2. Outcome is continuous bounded JSD under the frozen family; no
   Logit-dichotomized proxy.
3. Two-sided framework; all three β3 signs scientifically admissible.
4. Strict 2002 temporal boundary; old ladder demoted to sensitivity.
5. MIRCA2000 crop-calendar exposure is primary; thermal rule renamed
   "thermal-season climatic displacement", robustness only.
6. "Spatial-block bootstrap" renamed honestly: primary = M49-subregion
   cluster bootstrap; a true tile-based spatial block bootstrap is the
   secondary method.
7. Portfolio robustness gated at share_coverage ≥ 0.70.
8. Machine-readable `PRIMARY_ANALYSIS_LOCK.yaml` + SHA-256.

## Frozen stack (summary)

- Sample: `primary_sample_preoutcome.csv`, N=147.
- Model: fractional logit `y = jsd/√ln2` on `[1, HHI, M, HHI·M]`,
  standardized HHI/mismatch.
- Inference: subregion cluster bootstrap, B=999, two-sided 95% CI,
  seed 20261003.
- Contrasts: ME(+1 SD mismatch) at HHI P25/P50/P75; Δ_ME = P75−P25.
