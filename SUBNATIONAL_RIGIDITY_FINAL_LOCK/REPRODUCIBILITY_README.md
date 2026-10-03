# REPRODUCIBILITY — SUBNATIONAL RIGIDITY FINAL LOCK

## Pipeline order

```
scripts/40_admin_coverage.py        # observation matrix
scripts/41_crop_taxonomy.py         # crop ontology
scripts/42_boundary_harmonization.py
scripts/43_design_matrix.py         # vintages, shares, JSD
scripts/44_irrigation_zonal.py      # SPAM2010 (robustness) + USDA I1
scripts/45_mismatch.py              # POWER centroids + MIRCA calendars
scripts/47_repair.py                # v2: SPAM2000 baseline irrigation,
                                    #     temporal alignment audit,
                                    #     calendar proxy validation,
                                    #     final_primary_design_matrix_preoutcome.csv
scripts/48_spatial_blocks.py        # spatial blocks + geometry
scripts/information_simulation_v2.py# spatial inference sim v2 + info sim v2
```

Requires `data/raw/` (excluded from the public mirror): GADM 4.1,
HarvestStat v1.2, FAO subnational, Eurostat apro_cpshr, StatCan, USDA
census, IBGE PAM, MapSPAM 2000/2010, MIRCA2000, NASA POWER cache.
All sources and checksums: `DATA_SOURCE_LEDGER_v2.csv`.

## Frozen artefacts

- `SUBNATIONAL_PRIMARY_ANALYSIS_LOCK_v2.yaml` (+`.sha256`)
- `analysis/final_primary_design_matrix_preoutcome.csv` — 369 units;
  contains no fitted objects, only observed variables
- `analysis/admin_spatial_blocks.csv` — frozen block assignments
- `12_COVARIATE_PROTOCOL_v2.csv`

## What is deliberately absent

No estimate of β3 or any exposure×outcome association. The next phase
fits the locked model once, on this matrix, with B=999 block bootstrap,
seed 20261003.
