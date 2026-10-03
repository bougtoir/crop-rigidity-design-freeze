# 04 Robustness report

`analysis/ROBUSTNESS_LEDGER.csv` — every prespecified analysis,
no selection.

| analysis | β3 | 95% CI | p |
|---|---|---|---|
| primary OLS grid10 | −0.0377 | [−0.251, +0.077] | 0.38 |
| fractional-logit GLM | −0.249 (link scale) | — | — |
| grid15 blocks | −0.0377 | [−0.253, +0.093] | 0.37 |
| kmeans blocks | −0.0377 | [−0.217, +0.059] | 0.40 |
| SPAM2010 irrigation (N=314) | **+0.2235** | **[+0.004, +0.675]** | **0.046** |
| NUTS2 sensitivity (N=373) | −0.0283 | [−0.204, +0.137] | 0.53 |
| + HHI control | −0.0441 | [−0.260, +0.078] | 0.34 |
| + log(area) control | −0.0585 | [−0.294, +0.034] | 0.21 |
| LOCO | range −0.105 … −0.014 | — | — |
| LORO | range −0.066 … −0.007 | — | — |

## Honest read

* The frozen primary specification and every block scheme, the NUTS2
  scope, mechanism and precision controls, and all 23 leave-one-out
  fits agree: small negative, null-compatible interaction.
* **One prespecified sensitivity diverges:** SPAM2010 irrigation
  (measured ~2010, mid-window, N=314) gives β3 = +0.22, p = 0.046.
  SPAM2000 (baseline, pre-outcome) is the frozen exposure for temporal
  priority; the SPAM2010 divergence is reported, not suppressed. It
  signals exposure-vintage sensitivity — possibly post-treatment
  irrigation absorbing treatment effects — and is a disclosed
  instability, weighted into the classification in
  `08_RESULT_CLASSIFICATION.md`.
