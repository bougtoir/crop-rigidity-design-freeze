# Reproducing CROP_RIGIDITY_PRIMARY_RESULTS

Pipeline order (from `crop_rigidity_design_freeze/`):

1. `python3 scripts/20_primary_analysis.py`
   - verifies `PRIMARY_ANALYSIS_LOCK.yaml` SHA-256 (aborts on mismatch)
   - builds the locked N=147 sample → `analysis/PRIMARY_ESTIMATION_SAMPLE_LOCKED.csv(.sha256)`
   - standardized fractional-logit fit → `analysis/PRIMARY_FIRST_OPENING.json(.sha256)`
   - subregion cluster bootstrap B=999 seed 20261003 → `analysis/primary_bootstrap_replicates.csv`
   - `analysis/primary_model_results.csv`, `analysis/primary_effects.csv`
   - caches `_cache_{est.parquet,y.npy,X.npy,meta.json}` for downstream scripts
2. `python3 scripts/21_aux_mismatch.py` → `analysis/aux_mismatches.csv`
   (primary / old_ladder / lagged / pre_treatment / future exposure variants)
3. `python3 scripts/22_full_analysis.py` → figures + `analysis/secondary_inference.json`
   (re-runs the identical bootstrap storing full parameters for bands)
4. `python3 scripts/23_robustness_falsification.py` → `analysis/robustness_specification_ledger.csv`
5. `python3 scripts/24_falsification_subgroups.py` → `analysis/falsification_results.csv`,
   `analysis/subgroup_exploratory_results.csv`, `analysis/leave_region_out.csv`,
   `analysis/leave_subregion_out.csv`
6. `python3 scripts/25_package.py` → `PACKAGE_MANIFEST.csv` + `CROP_RIGIDITY_PRIMARY_RESULTS.zip`

Upstream inputs (built in the FINAL_LOCK phase, scripts `11_final_lock_inputs.py`
and earlier — see `CROP_RIGIDITY_FINAL_LOCK/REPRODUCIBILITY_README.md`):
FAOSTAT QCL crop-mix (OWID mirror 2026-02-25), NASA POWER monthly climate
parquets, SPAM2000 harvest footprints, MIRCA2000 condensed cropping
calendars + unit-code grid. Raw data live under `data/raw/` and are not
redistributed; reacquire via `scripts/00_acquire_data.py`.

Determinism: all resampling uses `np.random.default_rng(20261003)`;
the only stochastic steps are the bootstrap draws and the F3/F10
permutations (same seed). Standardization moments are the locked-sample
values recorded in `PRIMARY_FIRST_OPENING.json`.

Environment: python 3.10, pandas, numpy, statsmodels ≥0.15, matplotlib, pyarrow.
