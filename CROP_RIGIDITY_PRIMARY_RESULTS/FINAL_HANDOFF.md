# FINAL HANDOFF — CROP_RIGIDITY_PRIMARY_RESULTS

## Verdict

**β3 = +0.0046, 95% CI [−0.131, +0.143]** (subregion cluster bootstrap,
B=999/999 valid, seed 20261003). Frozen effects: Δ_ME = +0.0007 JSD
[−0.018, +0.021]. **RESULT B — null-weak conditioning.** NATURE PATH: not
viable for this analysis.

## Protocol execution summary

| Phase | Status |
|---|---|
| 0. Lock SHA-256 verification | PASS (`7b7f68e9…3143c47d`, `00_LOCK_VERIFICATION.md`) |
| 1. Sample materialization | PASS (N=147, SHA-256 `d16af0fe…ef315f`) |
| 2. Exact variable construction | PASS (frozen moments saved in FIRST_OPENING.json + `_cache_meta.json`) |
| 3. First β3 fit + opening record | PASS (written before any other fit) |
| 4. Bootstrap B=999 | PASS (999/999 valid) |
| 5. Frozen effect contrasts | PASS |
| 6. Four figures | PASS |
| 7. Secondary inference | PASS (tile block boot + HC2, post-opening) |
| 8. Robustness ledger (9 specs) | PASS |
| 9. Falsifications (10 rows) | PASS — F2 flagged positive, reported verbatim |
| 10. Exploratory subgroups | PASS (labeled exploratory, no rescue) |
| 11. Classification | RESULT B |
| 12. Claim audit | PASS — no forbidden claims; F2 discordance disclosed |
| 13. Nature viability | NOT VIABLE — redirect required |
| 14. Packaging | this package + zip + manifest |

## Numbers that define the result

- y = JSD/√ln2; standardized predictors; fractional logit.
- β1 (HHI main effect) = −0.102; β2 (mismatch) = −0.011; β3 = +0.005.
- Marginal effect of +1 SD mismatch on JSD at HHI P25/P50/P75:
  −0.0020/−0.0017/−0.0012, all CIs covering 0.
- Secondary: tile block boot [−0.186, +0.105]; HC2 [−0.422, +0.431].

## Files

- `00_LOCK_VERIFICATION.md`, `01_SAMPLE_VERIFICATION.md` — gates.
- `02_PRIMARY_RESULT.md` … `08_NEXT_PHASE_RECOMMENDATION.md` — the audit trail.
- `analysis/` — locked sample (+sha), first opening (+sha), 999 bootstrap
  replicates (full parameter vector per replicate), model results, effects,
  robustness ledger, falsification results, subgroups, leave-one-out CSVs,
  auxiliary mismatch variants, secondary inference JSON.
- `figures/` — scatter, predictions (bootstrap bands), ME curve, forest.
- `scripts/` — `20_primary_analysis.py` (lock→fit→bootstrap),
  `21_aux_mismatch.py` (exposure variants), `22_full_analysis.py`
  (figures + secondary inference), `23_robustness_falsification.py`,
  `24_falsification_subgroups.py`, `25_package.py` (manifest + zip).
- `PRIMARY_ANALYSIS_LOCK.yaml` + `.sha256` — the executed lock.
- `PACKAGE_MANIFEST.csv`, `REPRODUCIBILITY_README.md`.

## Integrity notes

- FIRST_OPENING was written before any robustness/falsification ran.
- `primary_bootstrap_replicates.csv` was regenerated once with full
  parameter columns for figure bands — identical resampling scheme
  (seed 20261003, subregion draws); β3 column unchanged.
- No manuscript was drafted.
