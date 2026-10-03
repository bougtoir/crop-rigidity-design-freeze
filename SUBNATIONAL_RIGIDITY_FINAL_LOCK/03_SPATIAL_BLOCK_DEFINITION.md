# 03 SPATIAL BLOCK DEFINITION (frozen)

See `analysis/admin_spatial_blocks.csv` (+`_describe.csv`).

Blocks were defined **independently of outcomes** (pure geometry).

| Scheme | n blocks | units/block median | max | singletons | crosses country | median diameter |
|---|---|---|---|---|---|---|
| **grid10 (PRIMARY)** | 71 | 4.0 | 37 | 18 | 20 | 5.27° |
| kmeans6 (sensitivity) | 93 | 4.0 | 13 | 13 | 0 | 3.66° |

- **grid10**: 10°×10° lat/lon grid cells over unit centroids. Objective,
  outcome-free, but can straddle country borders (20 blocks) and has 18
  singleton blocks (resampled as units of one).
- **kmeans6**: within-country k-means on centroids, k=⌈units/6⌉.
  Never crosses country lines; retained as sensitivity block scheme.

## Frozen choice

**10°×10° grid block bootstrap** is the primary inference method
(resample whole blocks with replacement, refit the model each draw,
percentile-of-SD CI via bootstrap standard error of β3).

Rationale: best type-I calibration under moderate spatial correlation
(8.0% vs 24.7% for within-country pairs bootstrap, 22.0% country CRVE)
and it genuinely propagates spatially block-correlated dependence.
Residual anti-conservatism at ρ=1500 km (16.7%) is a disclosed
limitation — correlation at that scale is cross-continental and
unrealistic for crop-mix residuals.

Block size was fixed a priori (10°), not tuned for CI width.
