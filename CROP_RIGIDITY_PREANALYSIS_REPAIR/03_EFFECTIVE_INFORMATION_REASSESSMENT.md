# 03 — Effective Information Reassessment (power v2)

The v1 power analysis is superseded: it simulated a generic design
matrix, ignored clustering entirely, and must not be cited as evidence.
This version uses the **observed** Legacy HHI, the **observed**
mismatch built in `01_`, their observed joint distribution, the actual
estimation sample, and the actual UN M49 regional structure.

## Design of the reassessment

- Sample: N = **146** countries with observed mismatch, HHI, JSD, and a
  mapped region (estimation set).
- Clustering structure: 5 M49 regions, 19 M49 subregions.
- Model: fractional/binary logit with design matrix
  [1, L, M, L×M] on the observed standardized regressors; outcome
  simulated under the model only (no real outcome used).
- Inference methods compared: HC2 sandwich, region-clustered CRVE,
  pairs-cluster bootstrap by region, spatial-block bootstrap by
  subregion, leave-one-region-out (LORO) coefficient range.
- Effect sizes in marginal-effect units (`me_scale` ≈ 0.25·β3 for a
  logit).

## Results (analysis/power_simulation_v2.csv)

| β3 | HC2 | region CRVE | cluster boot | subregion block boot |
|----|-----|-------------|--------------|----------------------|
| 0.0  | 0.035 | **0.15** | 0.075 | 0.040 |
| −0.3 | 0.33  | 0.47  | 0.34  | 0.30  |
| −0.6 | 0.69  | 0.77  | 0.60  | 0.60  |
| −1.0 | 0.99  | 0.95  | 0.81  | 0.94  |

(null row = empirical rejection rate at nominal 5% one-sided)

## Findings

1. **5-cluster CRVE is anti-conservative** (15% under the null at a 5%
   level). With only 5 M49 regions, clustering at region level alone
   cannot be the primary inference — this is the key correction to the
   v1 assessment.
2. **Subregion (19-block) spatial bootstrap is calibrated** (4% under
   null) and retains reasonable power; pairs-cluster bootstrap by
   region (8%) is next best.
3. **Honest power**: ~60% at β3 = −0.6 (marginal effect ≈ 0.15),
   ~80–95% at β3 = −1.0. Moderate interactions will not reach
   conventional significance; only large effects are detectable. This
   must shape claim strength, not the estimand.
4. **LORO stability** is reported per scenario (median coefficient
   range) as the pre-specified robustness display.

## Frozen inferential method

**Primary**: spatial-block bootstrap over M49 subregions (19 blocks,
Rademacher-free pairs resampling as implemented), reporting the
bootstrap CI on β3. **Secondary**: wild-cluster bootstrap by region
and HC2 as sensitivity. Region-CRVE alone is prohibited as the primary
claim — frozen before observing β3, as required.
