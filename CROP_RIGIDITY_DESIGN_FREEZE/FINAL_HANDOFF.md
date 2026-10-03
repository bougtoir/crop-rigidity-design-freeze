# Final handoff — crop-rigidity design freeze

## Gate

**DECISION: GO TO FULL ANALYSIS** (see `12_FULL_ANALYSIS_GATE.md` for the
12-criterion table and the attached conditions).

## Directory contents

- `00_QC_REPORT.md` — previous-package QC; all CSV defects fixed, zip rebuilt
- `01_UNIT_OF_ANALYSIS_DECISION.md` — Design A (country×crop×period) primary;
  MapSPAM grid arm demoted to validation (MapSPAM has ~2 epochs → cannot carry
  a transformation outcome)
- `02_LEGACY_VARIABLE_PROTOCOL.md` — primary legacy = HHI on 1981–2000; entropy
  /top-1/top-3 frozen robustness; inertia quarantined to a disjoint window
- `03_ENVIRONMENTAL_MISMATCH_PROTOCOL.md` — primary = Mahalanobis distance of
  2001–2020 climate from the legacy dominant crop's baseline niche
- `04_OUTCOME_PROTOCOL.md` — primary = JSD crop-mix distance; secondary =
  dominant-crop replacement (12.9% prevalence, low-power caveat); yield
  retention explicitly excluded
- `05_PRIMARY_ESTIMAND.md` — β3 on Mismatch×HHI; three-sided interpretation
  frozen; β3>0 is a result, not a failure
- `06_CAUSAL_GRAPH.md` + `06_COVARIATE_TABLE.csv` — every covariate classified
  (confounder/mediator/collider/precision/not justified)
- `07_MULTIVERSE_PROTOCOL.csv` — 22 frozen specs, P1 = primary
- `08_FALSIFICATION_PROTOCOL.md` — 10 frozen tests incl. future-exposure
  placebo and simulated-null band
- `09_COUNTERFACTUAL_PROTOCOL.md` — RO = V_flexible − V_retain; switching
  penalties 0/10/20/30% labelled as assumptions; T* reported only if curves
  cross
- `10_INFORMATION_ASSESSMENT.md` — simulation-based CI widths; binding
  constraint is clustered inference at ~7 macro regions, not N
- `11_NOVELTY_RECHECK.md` — novelty class B maintained; no prior global
  specialization×mismatch→transformation test found
- `12_FULL_ANALYSIS_GATE.md` — the gate
- `DATA_SOURCE_LEDGER_v2.csv`, `REFERENCES_v2.bib`, `REPRODUCIBILITY_README.md`

## Machine artifacts (repo subdir, alongside the package — see zip)

- `scripts/` — 00_validate_tables, 01_acquire_data, 02_design_diagnostics,
  03_build_ledger, 04_power_simulation
- `analysis/` — 00_qc_tables.csv, design_diagnostics_summary/globals,
  power_simulation.csv
- `data/raw/` — FAOSTAT QCL feather, MapSPAM zips, GAEZ tifs+json, MIRCA zips,
  ISIMIP ncs, SPEI ncs; SHA-256 for all in the ledger

## Headline caveats for the next session

1. GAEZ public mirror has only 3 crops × 1 scenario × 2 periods — pull more via
   the Data Portal or lean on the ISIMIP3b GGCM panel for the counterfactual.
2. FAOSTAT was acquired through the OWID mirror (FAO hosts unreachable); the
   provenance is versioned and checksummed.
3. Effective N is bounded by ~7 macro regions → region-clustered bootstrap is
   mandatory; the binary secondary outcome is low-power (27 events).
4. Everything is frozen before the interaction is estimated: do not re-pick
   metrics or windows after seeing β3.
