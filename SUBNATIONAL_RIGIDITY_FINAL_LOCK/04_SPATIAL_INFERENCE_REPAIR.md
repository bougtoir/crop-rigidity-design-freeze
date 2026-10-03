# 04 SPATIAL INFERENCE REPAIR

`analysis/spatial_inference_simulation_v2.csv` — 150 null reps per scenario,
residuals ~ N(0, σ²·exp(−d_ij/ρ)) + country random effects, two-sided α=0.05.

Type-I error (empirical rejection of true zero):

| method | indep | weak (150 km) | moderate (500 km) | strong (1500 km) |
|---|---|---|---|---|
| HC3 | 0.020 | 0.067 | 0.167 | 0.240 |
| country CRVE | 0.207 | 0.140 | 0.220 | 0.280 |
| within-country pairs bootstrap (old) | 0.073 | 0.113 | 0.247 | 0.320 |
| **10° grid block bootstrap** | 0.047 | 0.067 | 0.080 | 0.167 |
| kmeans block bootstrap | 0.053 | 0.053 | 0.093 | 0.147 |

Median CI width (JSD units): grid10 0.49–0.60 — widest of the calibrated
methods, i.e. it honestly prices spatial dependence.

## Frozen decision

- **Primary: 10°×10° geographic block bootstrap**, B=999 at analysis time,
  seed 20261003, two-sided α=0.05.
- Sensitivity: kmeans block bootstrap, within-country pairs bootstrap
  (reported, expected narrower/anti-conservative under real spatial
  correlation), HC3 (descriptive only).
- Country CRVE and HC3 are demoted: anti-conservative under anything but
  independent residuals. Conley/spatial-HAC not implementable robustly in
  this toolchain — grid bootstrap chosen as the validated alternative.
- Limitation disclosed: at ρ=1500 km all methods degrade; grid bootstrap
  remains least-worst (16.7%). Such cross-continental residual
  correlation is not plausible for this design after country FE.
