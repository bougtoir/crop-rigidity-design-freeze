# 11 FINAL LOCK REPORT

Repair audit closed. The v1 GO was issued on a premature lock; all nine
issues are resolved or explicitly disclosed, and a new lock
(`SUBNATIONAL_PRIMARY_ANALYSIS_LOCK_v2.yaml`) is written and checksummed.

## What changed substantively

- **Exposure era**: irrigation capital is now measured at ~2000
  (SPAM2000 zonal), preceding the transformation window. This is the
  theoretically required ordering: capital must precede the
  transformation it is hypothesized to constrain.
- **Inference**: within-country pairs bootstrap (non-spatial) replaced
  by a real 10°×10° geographic block bootstrap, validated under
  exponential spatial correlation (ρ=1–1500 km).
- **Information simulation**: rebuilt with analytically known generating
  truth on the JSD scale.
- **Model lock**: one primary formula, covariates reclassified.
- **Sample**: 369 units / 38 countries / 5 regions, all completeness
  rules applied; 92 units dropped under the locked missingness rule
  (missing baseline irrigation or geometry), never for outcome reasons.

## Residual limitations (disclosed, not hidden)

- Under ρ=1500 km residual correlation, type-I ≈16.7% for the frozen
  method (least-worst of six; plausible correlation at that scale after
  country FE is unlikely).
- H_PERENNIAL remains under-powered.
- MIRCA calendar national approximation validated but an approximation.
- Missing-major-region coverage binds scope to multi-region.

## Gate

DECISION: **GO TO SUBNATIONAL PRIMARY ANALYSIS** (multi-region scope).
The real interaction has never been estimated.
