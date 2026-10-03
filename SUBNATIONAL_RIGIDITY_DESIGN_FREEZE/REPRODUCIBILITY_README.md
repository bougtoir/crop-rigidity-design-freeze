# Reproducibility

Order of scripts (all under ../scripts/, run from repo crop_rigidity_design_freeze/):
1. 40_admin_coverage.py — builds analysis/admin_crop_observation_matrix.parquet
   and admin_unit_coverage.csv from data/raw/subnat/*.
2. 41_crop_taxonomy.py — writes 04_CROP_CROSSWALK.csv.
3. 42_boundary_harmonization.py — writes ADMIN_BOUNDARY_CROSSWALK.csv and
   analysis/boundary_change_audit.csv (needs data/raw/subnat/gadm41_admin1_index.csv
   extracted from gadm_410-levels.gpkg layer ADM_1).
4. 43_design_matrix.py — analysis/design_matrix.csv, within_country_information.csv.
5. 44_irrigation_zonal.py — irrigation exposure; needs spam2010_H extracted
   rasters and the three boundary files.
6. 45_mismatch.py — POWER fetches cached under data/raw/power_subnat/.
7. 46_simulations.py — decomposition validation, spatial inference simulation,
   information simulation.
Raw data are NOT in the public mirror (third-party terms) — reacquire per
DATA_SOURCE_LEDGER.csv URLs.
