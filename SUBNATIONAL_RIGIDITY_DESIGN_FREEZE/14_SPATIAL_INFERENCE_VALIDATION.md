# 14 — Spatial inference validation (frozen method)

Simulation: block-correlated synthetic outcomes preserving admin geometry,
country clustering, and unequal unit counts (analysis/spatial_inference_simulation.csv,
300 replicates).

| method | type-I rate |
|--------|-------------|
| HC3 iid | 4.0% |
| country cluster CRVE | 15.7% (anti-conservative) |
| within-country block bootstrap | 6.7% |
| Conley | not implemented (geometry proxy only) |

Frozen decision: **within-country unit block bootstrap** (pairs resampled inside
country, B>=999 at run time, seed locked) as primary inference; country-cluster
CRVE reported as anti-conservative benchmark. Two-sided alpha 0.05.
