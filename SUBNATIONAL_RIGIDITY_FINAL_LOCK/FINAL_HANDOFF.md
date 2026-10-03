# FINAL HANDOFF — SUBNATIONAL RIGIDITY FINAL LOCK

**DECISION: GO TO SUBNATIONAL PRIMARY ANALYSIS (multi-region scope)**

## Next action (when instructed)

Single execution of the locked primary analysis:

```
JSD ~ irr_share_base2000 + mismatch_T + irr_share_base2000×mismatch_T + country FE
```

- matrix: `analysis/final_primary_design_matrix_preoutcome.csv`
- inference: 10°×10° block bootstrap (`analysis/admin_spatial_blocks.csv`),
  B=999, seed 20261003, two-sided α=0.05
- then predefined: mechanism-control (+HHI), precision (+log area),
  secondary perennial/HHI hypotheses, Kitagawa decomposition
  (descriptive), robustness set incl. R-IRR-2010, R-CAL-SUBNAT,
  kmeans blocks, pairs bootstrap.
- no further design edits after the fit.
