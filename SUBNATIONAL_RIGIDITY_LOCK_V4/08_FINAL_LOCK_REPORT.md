# 08 Final lock report — SUBNATIONAL RIGIDITY V4

* `analysis/PRIMARY_SUBNATIONAL_SAMPLE_LOCKED_V4.csv` (+ sha256):
  340 strict first-level units / 23 countries / 4 regions.
* `SUBNATIONAL_PRIMARY_ANALYSIS_LOCK_V4.yaml` (+ sha256): strict
  geography, unit IDs, countries, N, scope, irrigation source, mismatch,
  windows, outcome, OLS + country FE, grid10 blocks, B=999, seed,
  two-sided α, primary interaction and JSD-scale contrast, robustness,
  NUTS2 sensitivity, HHI mechanism control, perennial secondary,
  H4 decomposition.
* `analysis/{jsd_marginal_summary_v4, admin_spatial_blocks_v4,
  information_simulation_v4, spatial_inference_simulation_v4}.csv`.
* `scripts/{information_simulation_v4, spatial_inference_v4,
  package_validation_v4}.py`.

Gate: all 11 conditions PASS → **GO TO SUBNATIONAL PRIMARY ANALYSIS**.

Residual disclosures: Europe out of primary (data/geography reality);
power asymmetric on the bounded grid (0.57–0.98); induced JSD null
projection −0.0046 reported. v3 artifacts untouched.
