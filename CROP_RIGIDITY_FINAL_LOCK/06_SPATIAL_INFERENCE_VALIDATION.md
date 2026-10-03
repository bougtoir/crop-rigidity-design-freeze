# 06 — Spatial inference validation (Issues 6 + 7)

## Terminology correction

The previous "spatial-block bootstrap" resampled M49 **subregions** as
clusters — it is a **subregion cluster bootstrap**, not a spatial-block
algorithm. Terminology corrected everywhere; the genuine spatial-block
bootstrap (predefined 30°×30° lat-lon tiles from country centroids) is
implemented and evaluated separately.

## Design

200 simulations per scenario on the real primary design (N=147,
fractional-logit family, two-sided α=0.05). Outcomes generated with
latent noise correlated as `exp(-d/s)` over haversine centroid
distances: s = 0 (none), 500 (weak), 1500 (moderate), 4000 km (strong).
The prior simulation's independent-residual DGP could not have
established spatial robustness; this one can.

## Results (`analysis/spatial_inference_simulation.csv`, type-I at 5%)

| method | none | weak | moderate | strong |
|--------|------|------|----------|--------|
| HC2 | 0.000 | 0.000 | 0.000 | 0.000 |
| region CRVE (5 clusters) | failed | failed | failed | failed |
| **subregion cluster bootstrap** | 0.060 | 0.075 | 0.060 | 0.050 |
| Conley SE (1500 km) | 0.150 | 0.145 | 0.170 | 0.165 |
| spatial block bootstrap (30° tiles) | 0.045 | 0.035 | 0.050 | 0.035 |

Notes: HC2 is degenerate-conservative here (CI width 0.85 vs 0.15 — the
sandwich blows up on the bounded outcome); region CRVE fails outright
(5 clusters insufficient). Conley is anti-conservative (~15% under the
null) — excluded from primary inference.

## Frozen inferential stack (two-sided, α = 0.05, 95% CI)

- **Primary: M49-subregion cluster bootstrap** (pairs bootstrap
  resampling whole subregions; percentile 95% CI; B = 999 in the
  analysis run).
- **Secondary: geographic block bootstrap** (predefined 30° lat-lon
  tiles; mildly conservative: 3.5–5.0%).
- HC2 reported only as a conservative bound. Conley and region-level
  CRVE prohibited as primary.
