# 09 Final lock report — SUBNATIONAL RIGIDITY V3

## Delivered

* `analysis/PRIMARY_SUBNATIONAL_SAMPLE_LOCKED.csv` (+ `.sha256`) —
  373 units / 28 countries / 5 regions, every unit admin-1-equivalent.
* `SUBNATIONAL_PRIMARY_ANALYSIS_LOCK_v3.yaml` (+ `.sha256`) — freezes
  unit IDs, level, countries, irrigation source, mismatch definition,
  temporal windows, outcome, estimator, country-FE structure, block
  scheme, bootstrap (B=999), seed, two-sided α, missingness rules,
  primary contrast, secondary hypotheses, robustness set, scope label.
* `analysis/admin_spatial_blocks_v3.csv` — grid10/grid15/kmeans blocks
  rebuilt on the locked sample.
* `analysis/spatial_inference_simulation_v3.csv` — type-I calibration:
  grid10 PASS in all scenarios.
* `analysis/information_simulation_v3.csv` — blind sim; exact null;
  bias≈0; coverage 96.5–98.5%; power 1.0 at |b3|≥0.15.
* `analysis/spatial_scale_diagnostics.csv`, `median_area_by_country.csv`,
  `sample_attrition_v3.csv`.
* `scripts/` — spatial_scale_harmonization.py, final_sample_v3.py,
  information_simulation_v3.py, spatial_inference_v3.py,
  package_validation.py.

## Gate

All 12 final-gate conditions pass → **GO TO SUBNATIONAL PRIMARY
ANALYSIS (multi-region)**. The real interaction coefficient remains
unestimated; the next phase is the single prespecified opening.

## Known residual limitations (disclosed, not blocking)

* Eurostat regional baseline crop-mix is sparse pre-2010: Europe
  contributes only 33 units/5 countries; the design is SSA-heavy by
  data availability, as documented since the multi-region scope call.
* Burkina Faso GADM-based rows were replaced by HarvestStat duplicates
  via the predeclared dedup rule (same physical regions).
* `GADM:IDN.15_1` has no GADM-4.1 polygon and stays excluded.
