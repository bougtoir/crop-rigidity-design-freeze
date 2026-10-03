# FINAL HANDOFF — SUBNATIONAL_RIGIDITY_FEASIBILITY

## Verdict

**DECISION: CONDITIONAL GO — GLOBAL SUBNATIONAL STUDY (admin-1 design).**

The new question — does *spatially fixed* legacy capital (irrigation,
perennial capital, persistent crop geography) × climatic mismatch govern
*local* transformation — is novel, testable, and its potential positive
result would explain rather than contradict the archived national null.

## Essentials

- **Unit: harmonized admin-1** fed by observed statistics (GSAP /
  Agro-MAPS / FAO subnational / SPAM open inputs). Pixel-level
  cross-vintage outcomes rejected — pilot shows vintage-to-vintage model
  noise dominates below ~0.5°.
- **Exposures (separate, not composite):** irrigation dependence
  (physically interpretable), perennial-crop share (switching-cost
  gradient), local HHI (continuity control). Exactly the "fixed capital,
  not specialization per se" contrast the programme needs.
- **Outcome:** local JSD/disappearance/entry plus the T = W + B
  decomposition for H4 — national change = within-unit switching +
  between-unit reallocation.
- **Mismatch:** same locked construction as the national study (MIRCA
  crop-calendar seasonal Mahalanobis, POWER/SPEI), ported to unit
  footprints.
- **Pilot numbers:** wheat pixel corr 0.84, gone 14%/new 26%, L1 0.23;
  at 0.5° L1 0.13; national |Δ| 5.4 Mha vs pixel churn L1 0.23 — the
  aggregation-escape signature is real in the data.

## Carried-forward conditions

1. Run the admin coverage/harmonization audit (countries × vintages ×
   boundary stability) before any design freeze.
2. No composite fixed-capital index.
3. Inherit the national falsification suite; add a method-change
   placebo (vintage-boundary discontinuity) and the within-country
   swap-pair audit.
4. National package stays frozen; do not merge samples.

## Package contents

`00_EXECUTIVE_DECISION`, `01_NOVELTY_AUDIT` + matrix, `02_SPATIAL_DATA_AUDIT`
+ unit decision, `03_LEGACY_CAPITAL_AUDIT`, `04_TRANSFORMATION_DECOMPOSITION`,
`05_MISMATCH_PROTOCOL`, `06_HYPOTHESIS_FEASIBILITY`,
`07_IDENTIFICATION_RISK_REGISTER`, `08_PILOT_REPORT`, `09_NATURE_LEVEL_DECISION`,
`DATA_SOURCE_LEDGER.csv`, `REFERENCES.bib`, `analysis/spam_vintage_pilot.json`,
`scripts/30_spam_vintage_pilot.py`, `REPRODUCIBILITY_README`.
