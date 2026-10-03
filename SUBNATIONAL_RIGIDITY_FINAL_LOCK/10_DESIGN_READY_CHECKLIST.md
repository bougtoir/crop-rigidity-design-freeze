# 10 DESIGN-READY CHECKLIST (machine-checkable)

| # | Condition | Status | Evidence |
|---|---|---|---|
| 1 | Primary irrigation exposure genuinely baseline/pre-outcome | PASS | `02_PRIMARY_IRRIGATION_DECISION.md` — SPAM2000 (~2000) precedes every endline |
| 2 | No SPAM2010 as primary | PASS | demoted to robustness R-IRR-2010 |
| 3 | Real geographic blocks or validated alternative frozen | PASS | `analysis/admin_spatial_blocks.csv`, `03` doc |
| 4 | Null type-I calibrated | PASS | `spatial_inference_simulation_v2.csv` — grid bootstrap 4.7–8.0% (weak–moderate); 16.7% strong = WARNING disclosed |
| 5 | CI coverage ≈ nominal | PASS | 0.92–1.00 in both simulation suites |
| 6 | Information simulation uses known generating coefficients | PASS | `information_simulation_v2.csv` — induced JSD-scale truth, bias≈0 |
| 7 | Primary model internally consistent | PASS | `06_PRIMARY_MODEL_RECONCILIATION.md`; covariate protocol updated |
| 8 | Climate windows match agricultural windows per unit | PASS | `admin_temporal_alignment_audit.csv` — all aligned=True |
| 9 | MIRCA national-calendar approximation audited | PASS | `calendar_proxy_validation.csv` — corr 0.992 |
| 10 | Checklist complete | PASS | this file |
| 11 | Scope = multi-region | PASS | binding label; India/China/Russia/Australia/Argentina/Mexico/MENA absent |
| 12 | Real β3 never estimated | PASS | no fit on `final_primary_design_matrix_preoutcome.csv` |
| 13 | Final sample ≥30 countries, ≥4 regions, several hundred units | PASS | 38 countries, 5 regions, 369 units |
| 14 | Lock v2 written + sha256 | PASS | `SUBNATIONAL_PRIMARY_ANALYSIS_LOCK_v2.yaml` |
