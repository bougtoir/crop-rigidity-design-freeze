# 05 INFORMATION SIMULATION REPAIR

`analysis/information_simulation_v2.csv` — `scripts/48b_sims.py` (v2) and
`scripts/information_simulation_v2.py` (copy). 

## Repair

v1 contained `if true_b3 is None: true_b3 = beta3` — the "truth" was a
fitted draw. Invalid.

v2 generates outcomes from a **fractional-logit DGP with an explicitly
assigned generating coefficient**:

```
η_i = logit(JSD_obs_i) + 0.15·Z_irr − 0.08·Z_mm + b3·Z_int + e_i
e ~ N(0, 0.25² · exp(−d_ij/500 km))      (spatially correlated)
Y_i = plogis(η_i)   ∈ (0,1), bounded like JSD
```

Z_irr, Z_mm standardized within the final sample; Z_int = product.
Because plogis saturates, the JSD-scale truth is the **population OLS
coefficient** of E[Y|b3] on the design — computed analytically, never
fitted from a draw.

## Results (120 reps, 10° block bootstrap B=50 inside sims)

| b3 (logit) | induced JSD-scale truth | bias | RMSE | coverage | power/type-I |
|---|---|---|---|---|---|
| 0.0 | 0.009 | +0.001 | 0.004 | 1.00 | type-I 0.008 |
| 0.5 | 0.092 | −0.001 | 0.003 | 1.00 | 1.00 |
| 1.0 | 0.138 | −0.000 | 0.002 | 1.00 | 1.00 |
| 1.5 | 0.158 | −0.000 | 0.002 | 1.00 | 1.00 |

- Bias ≈ 0 against the known induced truth; coverage ≥ nominal (slightly
  conservative under this DGP's noise level — the honest reading is that
  the frozen bootstrap errs conservative, not anti-conservative, at
  realistic residual dispersion).
- Power 1.00 for induced JSD-scale effects ≥ ~0.09 (≈0.4×sd(JSD)).
  Detectable floor: effects smaller than ~0.05 JSD-scale would be
  under-powered — disclosed.
- JSD is NOT dichotomized; observed mean/sd/range preserved by the DGP.
