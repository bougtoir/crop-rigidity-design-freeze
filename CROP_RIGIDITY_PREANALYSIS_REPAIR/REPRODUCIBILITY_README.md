# Reproducibility — CROP_RIGIDITY_PREANALYSIS_REPAIR

## What this package is

The final pre-analysis repair of the crop-rigidity design: it fixes
post-treatment leakage (SPAM2000 footprint), builds the Mahalanobis
climate mismatch on real data, audits the crop taxonomy and country
mapping, reassesses power with real inputs and clustered inference,
and freezes every remaining analytic choice **before** the primary β3
hypothesis test. No β3 is estimated here and no manuscript is drafted.

## Contents

- `00_TEMPORAL_LEAKAGE_REPAIR.md` — SPAM2000 footprint fix + frozen
  temporal ladder (incl. the documented 1984–2000 baseline deviation).
- `01_PRIMARY_MISMATCH_CONSTRUCTION.md` — Mahalanobis pipeline +
  diagnostics summary.
- `02_EXPOSURE_LEVEL_DECISION.md` — dominant vs portfolio decision.
- `03_EFFECTIVE_INFORMATION_REASSESSMENT.md` — power v2 + frozen
  inference method.
- `04_TEMPORAL_IDENTIFICATION_NOTE.md` — window-overlap admission +
  lagged sensitivity.
- `05_FINAL_PREANALYSIS_GATE.md` — the 10-criterion gate decision.
- `FAOSTAT_CROP_ITEM_AUDIT.csv` — item-level include/exclude table.
- `SPAM_FAOSTAT_CROSSWALK.csv` — FAOSTAT → SPAM2000 class map.
- `COUNTRY_REGION_CROSSWALK.csv` — FAOSTAT → ISO3/M49 map.
- `PACKAGE_MANIFEST.csv` — file inventory; verified by
  `scripts/05_validate_manifest.py`.
- `DATA_SOURCE_LEDGER_v3.csv` — every raw file: URL, version,
  retrieval time (UTC), bytes, SHA-256.
- `analysis/` — `corrected_cropmix_diagnostics.csv`,
  `footprint_cells.csv`, `primary_mismatch_country.csv`,
  `mismatch_diagnostics.csv`, `portfolio_mismatch_country.csv`,
  `power_simulation_v2.csv`, `power_fetch_log.csv`.
- `scripts/` — runnable pipeline (numbered).
- `FINAL_HANDOFF.md` — handoff contract for the analysis phase.

## Raw data

Per approach B, no raw data files are bundled in this package or the
public mirror. Everything under `data/raw/` is local-only; acquisition
URLs, versions, and SHA-256 checksums are in `DATA_SOURCE_LEDGER_v3.csv`.
To rebuild: run `scripts/01_acquire_data.py` (design-freeze package) for
the base corpora, plus the SPAM2000 dbf-csv/geotiff, ISIMIP
countrymasks, and the NASA POWER pulls performed by
`scripts/07_fetch_power_climate.py` (network access required; POWER
imposes a 10°×10° regional bbox and a 2° minimum span, one parameter
per request).

## Pipeline order

1. `06_repair_inputs.py` — item audit, corrected mix diagnostics,
   crop/country crosswalks, SPAM2000 footprint cells.
2. `07_fetch_power_climate.py` — NASA POWER monthly T/P per footprint
   cell (resumable; writes `data/raw/power/`).
3. `08_build_mismatch.py` — Mahalanobis mismatch + diagnostics +
   portfolio comparison.
4. `09_power_simulation_v2.py` — information reassessment.
5. `10_build_ledger_v3.py` — checksum ledger.
6. `05_validate_manifest.py` — manifest consistency check (exit 1 on
   any missing/extra file).
7. `00_validate_tables.py` (design-freeze scripts dir) — CSV format QC.
