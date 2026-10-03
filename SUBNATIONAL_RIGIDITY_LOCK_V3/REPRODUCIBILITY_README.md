# Reproducibility — SUBNATIONAL_RIGIDITY_LOCK_V3

All scripts run from the project root (`crop_rigidity_design_freeze/`)
with the data/raw tree in place. Order:

1. `scripts/49_scale_harmonization.py` (a.k.a. package
   `scripts/spatial_scale_harmonization.py`) — level audit, eligible-set
   construction, scale diagnostics. Emits `analysis/01_UNIT_LEVEL_AUDIT.csv`,
   `spatial_scale_diagnostics.csv`, `median_area_by_country.csv`.
2. `scripts/51_final_sample_v3.py` (`scripts/final_sample_v3.py`) —
   dedup, SPAM2000 zonal irrigation on deduped geometries, MIRCA/POWER
   mismatch fill (fetches any missing centroid JSONs into
   `data/raw/power_subnat/`), final lock + `.sha256` + attrition table.
   Requires network only when a POWER centroid is uncached.
3. `scripts/spatial_inference_v3.py` — blocks + type-I sims
   (`admin_spatial_blocks_v3.csv`, `spatial_inference_simulation_v3.csv`).
4. `scripts/information_simulation_v3.py` — blind info sim
   (`information_simulation_v3.csv`); byte-identical per run (fixed seeds).
5. `scripts/package_validation.py` — verifies both checksums and the
   byte-identical sim reproduction.

## Data provenance additions in v3

New raw inputs persisted under `data/raw/subnat/`:
`nuts2016_l{1,2}.geojson`, `nuts2010_l{1,2}.geojson` (GISCO NUTS
vintages 2016/2010, downloaded 2026-10-03, SHA-256 recorded in
`DATA_SOURCE_LEDGER_v3.csv`). New NASA POWER centroid JSONs (11 units)
under `data/raw/power_subnat/` — deterministic re-fetchable.

`data/raw/` stays local-only (public-data rule + third-party
redistribution); the mirror carries code and aggregated outputs only.
