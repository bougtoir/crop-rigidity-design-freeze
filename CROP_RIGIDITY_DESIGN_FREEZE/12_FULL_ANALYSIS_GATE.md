DECISION: GO TO FULL ANALYSIS

# 12 — Full-analysis gate

| Criterion | Verdict | Evidence |
|---|---|---|
| A. Data successfully downloaded | PASS (with routing caveat) | FAOSTAT QCL 9.1M rows via OWID mirror (FAO hosts unreachable from VM — mirror documented, versioned, checksummed); MapSPAM 2005+2010 geotiffs; GAEZ v4 SCI+YLDL (3 crops × 2 periods); MIRCA2000; SPEIbase 2.11; ISIMIP3b LPJmL × 2 GCMs; NASA POWER reachable |
| B. Primary outcome measurable | PASS | JSD computed on real data: median 0.126, p10–p90 0.078–0.213, N=210 |
| C. Primary mismatch measure defensible | PASS (construction pending) | Mahalanobis niche needs MapSPAM footprint × climate join — inputs acquired and verified readable; the metric itself is built in the full analysis, not assumed done |
| D. Legacy independent of outcome | PASS | HHI on 1981–2000 only; outcome on 2001–2020; inertia restricted to disjoint 1961–1980 window |
| E. Temporal ordering correct | PASS | frozen window ladder, no post-2000 predictors |
| F. N / effective N adequate | PASS for moderate+ effects | simulation: power ≈1.0 at β3≤−0.10; CI width ~0.07–0.23; region-clustered inference mandatory (small-cluster caveat carried forward) |
| G. Missingness manageable | PASS | ≥10yr/≥4-crop filter retains 210 units; sparse-reporting exclusion spec frozen (M01) |
| H. No fatal mechanical coupling | PASS | Dimension C quarantined; no outcome-window shares among predictors |
| I. Novelty defensible | PASS (class B) | no global specialization×mismatch→transformation test or specialization-conditional substitution counterfactual found |
| J. Primary model reproducible | PASS | all acquisition + diagnostics scripted; ledger with SHA-256 for every file |
| K. Multiverse frozen | PASS | 22 specifications, primary = P1 |
| L. Falsifications frozen | PASS | 10 tests incl. sharp placebos and simulated-null band |

## Conditions attached to the GO

1. **GAEZ coverage gap**: the public GCS mirror exposes only WHE/COT/SUC ×
   TP-2010/TP-2070 (ENSEMBLE, RCP8.5, irrigated high-input). The
   counterfactual arm must either (a) pull additional crops/scenarios via the
   GAEZ Data Portal during the analysis phase, or (b) rely on the ISIMIP3b
   GGCM yieldchange panel (≥2 GCMs already acquired; more SSPs enumerable).
   This does not block the observational estimand.
2. **FAOSTAT via OWID mirror**: the mirror is versioned (2026-02-25) and
   checksummed; the FAO bulk/API endpoints were unreachable from the VM.
   Provenance is documented; if a reviewer requires FAO-direct fetch, that is
   an environment constraint, not a data gap.
3. **Inference discipline**: all β3 inference uses region-clustered bootstrap;
   small cluster count is reported as a limitation.
4. **Three-sided admissibility preserved**: β3>0 is a result, not a failure;
   sign-reversal claims remain out of scope.

## What this gate does NOT authorize

- No manuscript drafting.
- No outcome-guided re-selection of mismatch metric, window, or crop set.
- No claim of "civilizational sign reversal".
