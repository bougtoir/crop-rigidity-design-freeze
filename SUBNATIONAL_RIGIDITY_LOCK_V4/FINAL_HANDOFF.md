# Final handoff — SUBNATIONAL RIGIDITY LOCK V4

**DECISION: GO TO SUBNATIONAL PRIMARY ANALYSIS (multi-region, strict first-level geography)**

* Strict sample: `analysis/PRIMARY_SUBNATIONAL_SAMPLE_LOCKED_V4.csv` —
  340 units / 23 countries / 4 regions, every unit a documented
  first-level administrative subdivision (+ sha256).
* Lock: `SUBNATIONAL_PRIMARY_ANALYSIS_LOCK_V4.yaml` (+ sha256).
* Bounded information sim calibrated to V4 marginal JSD (fractional
  logit + Beta, exact latent null); OLS + grid10 bootstrap type-I 5.0%,
  coverage 95.5% → OLS retained.
* Europe's NUTS2 statistical regions are outside primary and held as a
  prespecified sensitivity set.
* Blindness class A — the real subnational β3 has never been fitted.
* Next and final step: the single prespecified opening.
