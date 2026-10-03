# 07 — Effect-size interpretation (Issue 8)

β3 (log-odds interaction) is never reported alone. Frozen estimands
and contrasts, computed from the fitted fractional-logit model on the
primary sample — all defined BEFORE the model is run:

## Primary interpretable estimand

Expected change in JSD for a +1 SD increase in dominant-crop
crop-calendar mismatch, evaluated at:

- **low specialization**: HHI = P25 of the primary sample
- **median specialization**: HHI = P50
- **high specialization**: HHI = P75

Reported on the JSD scale (not log-odds), with two-sided 95% CIs from
the primary subregion cluster bootstrap.

## Headline contrast

`Δ_ME = ME(HHI = P75) − ME(HHI = P25)` — the difference in the
mismatch marginal effect between high- and low-specialization
countries, with its bootstrap 95% CI. This is the quantity the
"civilization constrains adaptation" hypothesis makes claims about;
sign-free interpretation (any of negative/zero/positive is a
scientifically admissible answer).

## Pre-registered plots

1. Fitted marginal effect of mismatch vs HHI percentile curve with
   bootstrap CI band.
2. JSD change per +1 SD mismatch at P25/P50/P75 HHI (point + CI,
   forest-style).
3. Scatter JSD vs mismatch, point size/color by HHI tercile.

No other post hoc contrasts are headline material; anything else is
labeled exploratory.
