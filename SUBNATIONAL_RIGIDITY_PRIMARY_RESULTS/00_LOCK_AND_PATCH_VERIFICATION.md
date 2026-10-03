# 00 Lock and patch verification

**LOCK_STATUS: VERIFIED**

* `PRIMARY_SUBNATIONAL_SAMPLE_LOCKED_V4.csv` SHA-256:
  `3894266f...069b03` — matches frozen record.
* `SUBNATIONAL_PRIMARY_ANALYSIS_LOCK_V4.yaml` SHA-256:
  `18e61718...6b37fe` — matches frozen record.

## Simulation patch (B)

`scripts/information_simulation_v4_1.py` corrects `contrast_for_b3()`:
the ±1 SD mismatch counterfactual now recomputes the interaction term
`z_int(mm±1) = (z_irr·(z_mm±1) − m0)/s0` with the frozen observed-product
standardization, instead of sign-flipping the observed interaction.
DGP, calibration, spatial structure, bootstrap, countries: unchanged.

## PATCH DECISION: PASS — OPEN PRIMARY ANALYSIS

| gate | result |
|---|---|
| null generating interaction exactly zero | PASS (0.0 by construction) |
| null type-I calibration | PASS (5.0%) |
| null CI coverage | PASS (95.5%) |
| effect mapping coherent | PASS (monotone; see 09_SIMULATION_PATCH_REPORT) |
| no unit-level JSD in DGP | PASS |
| no prior real β3 fit | PASS |

Unchanged copies of lock, lock sha, sample, sample sha are included in
this package.
