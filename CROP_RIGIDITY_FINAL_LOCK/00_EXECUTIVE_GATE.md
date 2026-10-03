# 00 — Executive gate (final lock)

| # | Gate criterion | Verdict | Evidence |
|---|----------------|---------|----------|
| 1 | Power/information analysis uses exactly the primary dominant-mismatch sample | PASS | `09_power_simulation_v3.py` reads `primary_sample_preoutcome.csv` (N=147, dominant calendar mismatch only) |
| 2 | Simulated outcome matches the continuous primary JSD model | PASS | bounded fractional-logit DGP; observed support/mean/dispersion/design matrix preserved; no dichotomization |
| 3 | Inference is two-sided | PASS | two-sided α=0.05 / 95% CI everywhere; symmetric β3 grid |
| 4 | Temporal boundary honestly resolved | PASS | strict 2002 boundary adopted primary; Δ-materiality negligible (03_, `temporal_boundary_diagnostics.csv`) |
| 5 | Crop-calendar choice resolved without β3 | PASS | MIRCA2000 CCC adopted on coverage/correlation grounds only (04_) |
| 6 | Portfolio robustness has defensible coverage threshold | PASS | ≥0.70 frozen; 0.50/0.80 pre-registered sensitivities (05_) |
| 7 | Spatial inference validated under spatially correlated simulation | PASS | `spatial_inference_simulation.csv`: subregion cluster bootstrap 5–7.5% across 4 dependence scenarios; Conley 15–17% excluded; block bootstrap conservative fallback |
| 8 | Effect-size contrasts frozen | PASS | `07_EFFECT_SIZE_INTERPRETATION.md` (P25/P50/P75 marginal effects + Δ_ME) |
| 9 | PRIMARY_ANALYSIS_LOCK.yaml exists and is checksummed | PASS | `PRIMARY_ANALYSIS_LOCK.yaml` + `.sha256` |
| 10 | β3 never estimated from real outcome data | PASS | no real-data interaction fit exists in this package |

## DECISION: GO TO PRIMARY ANALYSIS

Prior gate context preserved: novelty class B, no named law, forbidden
claims list unchanged; strongest defensible claim remains
*"Pre-existing production structure may condition the extent to which
crop systems reorganize under climatic mismatch."*
