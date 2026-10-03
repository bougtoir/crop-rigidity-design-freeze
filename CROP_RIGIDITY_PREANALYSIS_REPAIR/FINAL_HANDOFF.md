# FINAL_HANDOFF — crop rigidity, pre-analysis repair

## What the next phase receives

A repaired, leakage-free, fully specified pre-analysis package:

- **Exposure (frozen)**: dominant-crop Mahalanobis climate mismatch —
  `analysis/primary_mismatch_country.csv`. Portfolio-weighted
  alternative in `analysis/portfolio_mismatch_country.csv`
  (pre-specified robustness slot).
- **Estimation set**: 130 countries with finite mismatch; UN M49
  region/subregion attached via `COUNTRY_REGION_CROSSWALK.csv`.
- **Corrected legacy/outcome diagnostics**:
  `analysis/corrected_cropmix_diagnostics.csv` (post-taxonomy-audit
  HHI/JSD; supersedes `design_diagnostics_summary.csv` for analysis).
- **Inference (frozen)**: primary = M49-subregion spatial-block
  bootstrap on the fractional-logit interaction; secondary = wild
  region-cluster bootstrap and HC2. Region-level CRVE alone is
  prohibited (anti-conservative at 5 clusters).
- **Windows (frozen)**: legacy 1981–2000; footprint SPAM2000; climate
  baseline 1984–2000; exposure 2001–2020; outcome 1981–2000→2001–2020.
  Lagged sensitivity (2001–2010 exposure → 2011–2020 transformation)
  pre-specified as secondary.
- **Honest power**: ~0.60 at β3=−0.6 (marginal effect ≈0.15); ~0.9 at
  β3=−1.0. Moderate interactions may be indistinguishable from zero —
  a legitimate negative result.
- **Claim ceiling (Issue 9)**: class B; no named law; the forbidden
  claims list in `05_` binds the write-up.

## What the next phase must NOT do

- Do not re-open frozen choices (exposure level, mismatch metric,
  windows, inference method, regularization rule).
- Do not reintroduce MapSPAM 2005/2010 into the baseline.
- Do not silently re-add FAOSTAT aggregate items or FAO regional
  aggregates to the estimation set.
- Do not report β3 from a method other than the frozen inferential
  stack without declaring it exploratory.

## Provenance

All raw inputs are checksummed in `DATA_SOURCE_LEDGER_v3.csv`; none are
bundled (approach B). Rebuild path in `REPRODUCIBILITY_README.md`.
The design-freeze package `CROP_RIGIDITY_DESIGN_FREEZE/` remains the
upstream context; this repair supersedes it where they differ.
