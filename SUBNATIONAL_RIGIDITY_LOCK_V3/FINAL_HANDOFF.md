# Final handoff — SUBNATIONAL RIGIDITY LOCK V3

**DECISION: GO TO SUBNATIONAL PRIMARY ANALYSIS (multi-region)**

What this package is: the v3 final lock for the subnational study
"local fixed capital × climate mismatch → reduced local
transformational flexibility" (JSD of crop mix, admin-1 units).

* Sample: `analysis/PRIMARY_SUBNATIONAL_SAMPLE_LOCKED.csv` —
  373 units / 28 countries / 5 regions, checksummed.
* Lock: `SUBNATIONAL_PRIMARY_ANALYSIS_LOCK_v3.yaml` (+ sha256) —
  complete prespecification; real b3 never estimated.
* Inference: grid10 block bootstrap, B=999, seed 20261003 — calibrated
  type-I 3.5–6.5% across spatial-correlation strengths.
* Blindness: info simulation rebuilt fully outcome-blind (exact null
  1.3e-16); v2 class-B exposure disclosed in 04_BLINDNESS_AUDIT.md.
* Validation: `python scripts/package_validation.py` (checksums +
  byte-identical sim rerun).

Next phase (not this package): single prespecified opening —
estimate b3 once, bootstrap the frozen CIs, classify RESULT A–D.
