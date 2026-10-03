# 10 — Information / power assessment

## Nominal vs effective N

- Countries in estimable frame (both windows, ≥10 yr, ≥4 crops): **210**
- Median distinct crops per country: 60; outcome (JSD) well-dispersed
  (median 0.126, p10–p90: 0.078–0.213).
- Legacy HHI well-dispersed (median 0.138, p10–p90: 0.083–0.256).

Effective N is bounded below nominal N by (a) spatial autocorrelation of
mismatch across neighbouring countries — inference must cluster/bootstrap at
~7 UN macro regions, so independent-climate-regime count is small; and
(b) FAO reporting heterogeneity (several states enter/leave reporting; the
sparse-reporting exclusion spec is frozen as M01).

## Simulation-based precision (scripts/04_power_simulation.py → analysis/power_simulation.csv)

400 Monte-Carlo draws on the measured HHI distribution, JSD-scaled bounded
outcome, fractional-logit primary spec:

| scenario | true β3 | median 95% CI width | power@5% |
|---|---|---|---|
| null | 0 | 0.058 | 8.5% (size ≈ nominal, mild inflation noted) |
| small | −0.10 | 0.068 | 100% |
| moderate | −0.25 | 0.128 | 100% |
| large | −0.45 | 0.231 | 100% |

(Coefficient magnitudes are on the fractional-logit scale; the simulation
calibrates *precision*, and estimates on that scale are intentionally
conservative.)

## Consequences

1. Country-level Design A has ample power for moderate-to-large interactions;
   even small interactions are estimable with CI width ~0.07.
2. The **binding constraint is clustered inference**, not N: with ~7 macro
   regions, region-clustered bootstrap p-values are the honest ones, and
   leave-one-region-out (falsification #4) is the decisive robustness check.
3. Binary secondary outcome (dominant-crop replacement, 12.9% prevalence ≈ 27
   events) supports only large-effect interactions — report it as supporting
   evidence, never as a co-primary.
4. Emergence outcome (~1% prevalence) is unusable as an estimand; retained as
   descriptive only.
5. Grid-level Design B raises precision on climate exposure but cannot
   increase the number of independent policy-relevant units; it is validation,
   not a power rescue.
