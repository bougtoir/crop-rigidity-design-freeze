# 00 — QC report on previous package

## Scope

All CSV deliverables of `CIVILIZATION_ADAPTATION_FEASIBILITY/` were re-validated by
`scripts/00_validate_tables.py` (RFC4180 parse via python-csv AND pandas, UTF-8,
column-count consistency, duplicated headers/rows, empty identifier fields,
missing-value-token audit). Machine-readable results: `analysis/00_qc_tables.csv`.

## Defects found and fixed

| File | Defect | Fix |
|---|---|---|
| `01_novelty_matrix.csv` | 3 rows with 12 columns (unquoted commas split fields in "mechanism"/"data" columns) | stray commas merged back into the intended field; all 18 rows now 11 columns |
| `02_historical_data_audit.csv` | 7 rows with 19 columns (one missing column each) | missing cells restored at the correct column position (unit_of_analysis / sample_size / spatial_resolution); all 15 rows now 20 columns |
| `06_pilot_results.csv` | 3 rows with 9 columns (`ci95_hi` absent) | `NA` inserted in `ci95_hi`; all 10 rows now 10 columns |
| `DATA_SOURCE_LEDGER.csv` | 1 row with 13 columns (extra trailing field) | trailing field dropped; all 10 rows now 12 columns |
| `01_novelty_matrix.csv`, `04_future_counterfactual_audit.csv` | literal `none` used as a missing token | replaced with `NA` |
| `FINAL_HANDOFF.md` | stated `scripts/`, `analysis/`, `data/raw/` exist alongside but zip contents were ambiguous | handoff text corrected to state explicitly these live in the repo subdir and are NOT inside the zip |
| `CIVILIZATION_ADAPTATION_FEASIBILITY.zip` | built before the CSV fixes | rebuilt after the fixes |

## Post-fix state

All 7 CSVs now parse cleanly under pandas `read_csv` with zero errors, uniform
column counts, UTF-8 encoding, no duplicated headers or rows, no empty
identifier fields, and missing values restricted to `NA` / `n/a` / `-` / empty.

The QC script is idempotent and re-runnable: `python3 scripts/00_validate_tables.py`.

## Convention adopted for this package

All CSVs in `CROP_RIGIDITY_DESIGN_FREEZE/` use `NA` as the single missing-value
token and are validated by the same script before packaging.
