# Reproducibility — CROP_RIGIDITY_DESIGN_FREEZE

## Layout

    CROP_RIGIDITY_DESIGN_FREEZE/      deliverable documents + tables
    scripts/                          all acquisition & diagnostic code
    analysis/                         generated CSVs (QC table, diagnostics, power sim)
    data/raw/                         downloaded originals (per-source subdirs)

## Order of operations

    python3 scripts/00_validate_tables.py      # CSV QC (previous + this package)
    python3 scripts/01_acquire_data.py         # re-download any missing raw files,
                                               # verifies SHA-256, never overwrites
    python3 scripts/03_build_ledger.py         # regenerate DATA_SOURCE_LEDGER_v2.csv
    python3 scripts/02_design_diagnostics.py   # real-data diagnostics (FAOSTAT feather)
    python3 scripts/04_power_simulation.py     # Monte-Carlo CI widths for beta3

Dependencies: pandas, numpy, pyarrow, statsmodels, scipy, rasterio.
All randomness seeded (`numpy.default_rng(20261003)`).

## Data provenance

Every downloaded file is listed in `DATA_SOURCE_LEDGER_v2.csv` with URL,
version, DOI, license, access date, byte size and SHA-256. Two routing
constraints recorded honestly:

- FAOSTAT bulk/API hosts are unreachable from this VM → data acquired through
  the versioned OWID garden mirror (identical QCL content, version
  2026-02-25).
- ERA5/ERA5-Land require CDS credentials → substituted by ISIMIP W5E5 forcing
  (ERA5-family) and NASA POWER for country-level agroclimatology.

## Raw-data policy

Originals under `data/raw/` are never overwritten by re-acquisition
(`01_acquire_data.py` verifies checksums and refuses to clobber). The public
mirror of this project excludes `data/raw` where third-party licences
restrict redistribution (MapSPAM/GAEZ are handled per their terms; see the
sync workflow's EXCLUDE_MAP).
