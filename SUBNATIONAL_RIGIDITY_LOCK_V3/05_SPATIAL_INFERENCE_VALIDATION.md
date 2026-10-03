# 05 Spatial inference validation (v3, on locked sample)

Blocks rebuilt on the 373-unit locked sample (`scripts/spatial_inference_v3.py`,
seed 20261003). Type-I evaluated under exponentially spatially correlated
residuals (variance = observed JSD sd) plus country random effects,
200 replicates per scenario, 60 bootstrap resamples each.

## Block schemes (`analysis/admin_spatial_blocks_v3.csv`)

| scheme | n blocks | median units | max units | singletons | blocks crossing countries |
|---|---|---|---|---|---|
| **grid10 (primary)** | 67 | 3 | 36 | 19 | 15 |
| grid15 (sensitivity) | 49 | 4 | 58 | 10 | 17 |
| kmeans ceil(n/6) (sensitivity) | 75 | 5 | 11 | 3 | 0 |

## Type-I calibration (`analysis/spatial_inference_simulation_v3.csv`)

| scenario | rho_km | HC3 | country CRVE | **grid10 boot** | grid15 | kmeans |
|---|---|---|---|---|---|---|
| independent | 1 | .080 WARN | .205 FAIL | **.065 PASS** | .055 | .065 |
| weak | 150 | .045 | .160 FAIL | **.035** | .025 | .030 |
| moderate | 500 | .085 WARN | .205 FAIL | **.055** | .050 | .055 |
| strong | 1500 | .050 | .190 FAIL | **.035** | .030 | .040 |

Classification (PASS .03–.07 / WARNING .07–.10 / FAIL >.10):

* **grid10 block bootstrap: PASS in all four scenarios** — frozen as primary
  inference. Null coverage 93.5–96.5%.
* grid15 and kmeans also PASS — registered as sensitivity, not selected on
  result.
* Country CRVE FAILS (16–20.5% rejection under null) — excluded, as before.
* HC3 is borderline (2× WARNING) — retained only as a transparent
  non-spatial benchmark, never primary.

No strong-correlation FAIL remained after rebuilding on the harmonized
sample (v2's 16.7% worst case does not recur: v3 grid10 ≤6.5% everywhere),
so no escalation to larger blocks or spatial-HAC was required; grid15 is
nonetheless prespecified as a sensitivity check.
