# Reproducibility — CROP_RIGIDITY_FINAL_LOCK

Final blind design-lock package for "When civilization constrains
adaptation" (crop rigidity). Supersedes `CROP_RIGIDITY_PREANALYSIS_REPAIR`
where the two differ. Contains **no β3 estimate** — the primary
interaction has never been computed on real data.

## Contents

- `00_EXECUTIVE_GATE.md` — 10-criterion gate: GO TO PRIMARY ANALYSIS.
- `01_PRIMARY_SAMPLE_FLOW.{md,csv}` — attrition to the frozen N=147.
- `02_PRIMARY_MODEL_FAMILY.md` — fractional logit decision.
- `03_TEMPORAL_BOUNDARY_REPAIR.md` — strict 2002 boundary.
- `04_CROP_CALENDAR_AUDIT.md` — MIRCA2000 CCC adoption.
- `05_PORTFOLIO_COVERAGE_RULE.md` — ≥0.70 coverage floor.
- `06_SPATIAL_INFERENCE_VALIDATION.md` — inference freeze.
- `07_EFFECT_SIZE_INTERPRETATION.md` — frozen contrasts.
- `08_FINAL_LOCK_REPORT.md` — power v3 + frozen stack.
- `CROP_CALENDAR_CROSSWALK.csv` — SPAM→MIRCA class map.
- `PRIMARY_ANALYSIS_LOCK.yaml` + `.sha256` — the lock file.
- `PACKAGE_MANIFEST.csv`, `DATA_SOURCE_LEDGER_v4.csv`.
- `analysis/` — `power_simulation_v3`, `temporal_boundary_diagnostics`,
  `calendar_vs_thermal_mismatch`, `mismatch_diagnostics_v3`,
  `spatial_inference_simulation`, `primary_sample_preoutcome`,
  `primary_sample_flow`, `cropmix_diagnostics_v2`,
  `portfolio_mismatch_v3`, `portfolio_coverage`.
- `scripts/` — full pipeline (`00_acquire_data.py` …
  `12_build_ledger_v4.py`) plus `05_validate_manifest.py` (exit 1 on
  any missing/extra file).
- `FINAL_HANDOFF.md` — handoff contract to the analysis session.

## Raw data

Approach B: no raw data bundled. `DATA_SOURCE_LEDGER_v4.csv` checksums
every raw input (FAOSTAT feather, SPAM2000 zips + readme, MIRCA2000
zips, ISIMIP countrymasks, NASA POWER per-country parquets + raw JSON,
SPEI, GAEZ subset). Rebuild order:

1. `00_acquire_data.py` (repair package scripts; SPAM2000 + MIRCA +
   countrymasks), `01_acquire_data.py` (design-freeze base corpora).
2. `07_fetch_power_climate.py` — NASA POWER pulls (resumable).
3. `06_repair_inputs.py` — taxonomy audit, crosswalks, footprints.
4. `11_final_lock_inputs.py` — boundary diagnostics, calendar months,
   mismatches, sample.
5. `10_spatial_inference_validation.py` — inference validation.
6. `09_power_simulation_v3.py clboot_sub` — power/precision.
7. `12_build_ledger_v4.py`, `05_validate_manifest.py`.
