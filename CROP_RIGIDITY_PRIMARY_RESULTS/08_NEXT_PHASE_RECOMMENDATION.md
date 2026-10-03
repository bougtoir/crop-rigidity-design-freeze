# 08 — Next-phase recommendation

Primary analysis complete. β3 = +0.0046 [−0.131, +0.143] → RESULT B
(null-weak). NATURE PATH: not viable for this analysis.

## Ordered recommendations

1. **Do not iterate on this dataset.** The design discipline is spent:
   exposure, outcome, sample, and inference were frozen; refitting under a
   different spec against the same outcome would be post hoc by definition.
   Any follow-up must be a *new* pre-registered study.

2. **Candidate new registered designs, in order of expected signal:**
   a. **Subnational units** (FAOSTAT → GAEZ/MapSPAM pixel or admin-1):
      specialization–mismatch interactions plausibly live below the
      national aggregate; national HHI averages out within-country
      portfolios. Cost: new exposure data build.
   b. **Event-based outcome** (drought/price shocks → reallocation
      response, e.g. via SPEI + FAOSTAT year panels): the current outcome
      is a 20-year JSD — slow-moving; shock-response designs have more
      identifying variation.
   c. **Different legacy measure** (infrastructure, irrigation lock-in,
      varietal dependence) — HHI of crop shares is only one reading of
      "legacy dependence".

3. **F2 follow-up (no re-analysis)**: the positive pre-treatment flag is
   worth one registered check in the next design — a specialization
   variable measured *before* both windows, to separate drift from
   conditioning.

4. **Publication path now**: a short registered-report-format methods paper
   (pipeline + informative null) is honest and publishable in field
   journals; do not draft the Nature manuscript per the lock's instruction.

5. **Package disposition**: `CROP_RIGIDITY_PRIMARY_RESULTS/` is complete
   and hashed where required; archive as-is. No manuscript drafting was
   performed.
