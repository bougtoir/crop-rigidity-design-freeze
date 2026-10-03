# 03 Bounded DGP protocol

Theoretical support: JSD here is `sqrt` of the Jensen–Shannon divergence
computed with log2 → divergence ≤ 1 bit → distance ∈ [0, 1] exactly
(theoretical maximum 1.0; observed V4 max 0.954).

## Generating model (bounded by construction)

```
eta_i = alpha + g_country(i) + b1 z_irr + b2 z_mm + b3 z_int + s_i
mu_i  = plogis(eta_i)
Y_i ~ Beta(mu_i * phi, (1 - mu_i) * phi)
```

* `g_country` ~ N(0, 0.27²) fresh per replicate; `s` spatial Gaussian
  field, rho = 500 km, eta-scale SD 0.9.
* Calibrated moments (final-sample marginal only): `alpha = −1.05`,
  `phi = 30` → marginal mean 0.2895 (target 0.2932), SD 0.1743
  (target 0.1732). No zeros observed in-sample → no hurdle component.
* `b1 = 0.35`, `b2 = −0.20` assigned a priori on the link scale; never
  estimated from observed JSD.
* Unit-level observed JSD is used nowhere — only the five-number
  marginal summary in `analysis/jsd_marginal_summary_v4.csv`.

## Null exactness

Under b3 = 0 the generating-scale interaction is exactly 0
(<1e-16 by construction). Nonlinearity induces a JSD-scale OLS
projection interaction of −0.0046, two orders below the OLS standard
error (~0.03) — reported, not hidden.

## Estimand under OLS

The frozen estimator is OLS + country FE; its population target on the
JSD scale is the OLS projection of mu on the design, reported as
`induced_jsd_interaction` per scenario.
