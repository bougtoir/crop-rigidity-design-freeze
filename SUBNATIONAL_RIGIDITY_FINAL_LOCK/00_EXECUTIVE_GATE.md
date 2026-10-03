# 00 EXECUTIVE GATE — SUBNATIONAL FINAL LOCK

Independent-audit repair phase for `SUBNATIONAL_RIGIDITY_DESIGN_FREEZE`.
The prior GO was premature: three methodological defects were repaired
(post-baseline irrigation exposure, pseudo-block bootstrap, invalid
information-simulation truth) and five consistency issues resolved.

## Repairs applied

| Issue | Defect | Repair |
|---|---|---|
| 1 | Primary irrigation = SPAM2010 (inside outcome window) | Primary = **SPAM2000** zonal irrigated harvested-area share (reference yr ~2000); MIRCA2000 unit-level shares audited as fallback (not needed in final sample); SPAM2010 demoted to robustness |
| 2 | "Block bootstrap" resampled units, not spatial blocks | Real geographic blocks defined (10°×10° grid; within-country k-means); validated under exponential spatial correlation |
| 3 | `true_b3 = beta3` set truth to a fitted draw | Rebuilt: known logit-scale generating coefficient, induced JSD-scale truth computed analytically; metrics vs that truth |
| 4 | Primary model formula inconsistent vs covariate protocol | Reconciled: primary = `JSD ~ irr + mismatch + irr×mismatch + country FE`; HHI/perennial moved to mechanism-control/secondary |
| 5 | Climate/ag windows alignment unverified | Audited per unit: climate windows track each unit's actual y0/y1 ±1y smoothing |
| 6 | MIRCA national calendars as admin-1 proxy unaudited | Validated on US/Brazil/Indonesia subunits: national-vs-local mismatch corr 0.992 |
| 7 | Design-ready checklist empty | Rebuilt as machine-checkable `10_DESIGN_READY_CHECKLIST.md` |
| 8 | Kitagawa B-term terminology | B alone not called "escape"; |W|,|B|,|I| reported plus signed decomposition |
| 9 | Scope label | **MULTI-REGION** binding; "global" barred from empirical claims |

## Final sample (pre-outcome frozen)

- **369 admin-1 units, 38 countries, 5 regions** (SSA, Europe, North
  America, Latin America, South/Southeast Asia)
- All units carry SPAM2000 baseline irrigation exposure (0 MIRCA fills
  required in sample), MIRCA2000 crop-calendar mismatch, vintage-paired
  admin crop statistics (median gap 17 y).

## Gate conditions (12/12)

1. Primary irrigation exposure baseline/pre-outcome — **PASS** (SPAM2000)
2. No SPAM2010 primary — **PASS**
3. Real spatial blocks / validated alternative frozen — **PASS** (10° grid bootstrap)
4. Null type-I calibrated — **PASS** (grid bootstrap 4.7–8.0% at weak–moderate correlation; 16.7% at strong — disclosed limitation)
5. CI coverage ≈ nominal — **PASS** (0.92–1.00 across scenarios; conservative in low-noise DGP)
6. Information sim uses known generating coefficients — **PASS** (bias ≈ 0, RMSE ≤0.004 on JSD scale)
7. Primary model internally consistent — **PASS**
8. Climate/ag temporal alignment — **PASS**
9. MIRCA calendar approximation audited — **PASS** (corr 0.992)
10. Complete checklist — **PASS**
11. Scope multi-region — **PASS**
12. Real interaction never estimated — **PASS** (β3 untouched)

## DECISION: GO TO SUBNATIONAL PRIMARY ANALYSIS (multi-region scope)

Frozen in `SUBNATIONAL_PRIMARY_ANALYSIS_LOCK_v2.yaml` (+sha256).
The real exposure×outcome interaction remains un-estimated.
