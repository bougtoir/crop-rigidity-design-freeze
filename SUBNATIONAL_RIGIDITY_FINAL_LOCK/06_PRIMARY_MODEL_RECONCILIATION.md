# 06 PRIMARY MODEL RECONCILIATION (frozen)

The v1 lock formula conflicted with `12_COVARIATE_PROTOCOL.csv`.
Resolved as follows — one primary model, clearly separated satellites.

## PRIMARY MODEL (only confirmatory irrigation test)

```
JSD_i ~ irr_share_base2000_i + mismatch_T_i
        + irr_share_base2000_i × mismatch_T_i
        + country_FE
```

No HHI, perennial, or area adjustment. Justification per the frozen DAG
(12_CAUSAL_GRAPH.md): conditional on country, baseline HHI is a
descendant/collider-adjacent of the same structural drivers as irrigation
capital, not a necessary confounder of irrigation×mismatch; adjusting it
in the primary model would block part of the mechanism.

## MECHANISM-CONTROL MODEL (secondary, predefined)

Primary model + `hhi_baseline` — probes whether any interaction signal
operates through crop concentration rather than irrigation capital.

## PRECISION SENSITIVITY

Primary model + `log(area_baseline)`.

## SECONDARY EXPOSURE (separate hypothesis, not a covariate)

`perennial_strict` × `mismatch_T` in its own model — H_PERENNIAL remains
secondary and flagged under-powered.

## HHI-CONTINUITY CONTROL (H_HHI)

Crop-mix flexibility `JSD ~ hhi_baseline × mismatch_T + country FE` —
continuity check that the mechanism is specific to fixed capital, not
generic mix rigidity.

`12_COVARIATE_PROTOCOL.csv` is updated to match: hhi_baseline and
area_baseline reclassified mechanism-control/precision only;
perennial_strict is exposure, not covariate.
