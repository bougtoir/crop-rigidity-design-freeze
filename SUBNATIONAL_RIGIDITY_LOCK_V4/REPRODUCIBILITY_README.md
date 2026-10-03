# Reproducibility — SUBNATIONAL_RIGIDITY_LOCK_V4

Run order (from `crop_rigidity_design_freeze/`):

1. Strict sample + marginal summary + equivalence audit (already
   materialized in `analysis/`; regenerate via
   `scripts/51_final_sample_v3.py` then the strict filter that drops
   bare-NUTS unit_ids — see `analysis/01_EUROPE_ADMIN_EQUIVALENCE.csv`).
2. `scripts/spatial_inference_v4.py` → `admin_spatial_blocks_v4.csv`,
   `spatial_inference_simulation_v4.csv`.
3. `scripts/information_simulation_v4.py` →
   `information_simulation_v4.csv` (byte-identical; fixed seeds).
4. `scripts/package_validation_v4.py` → checksums, schemas, sim
   reproduction, blindness grep. Exit 0 required.
