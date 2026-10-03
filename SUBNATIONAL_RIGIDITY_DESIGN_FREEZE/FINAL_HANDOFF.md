# FINAL HANDOFF — SUBNATIONAL_RIGIDITY_DESIGN_FREEZE

Gate: GO TO SUBNATIONAL PRIMARY ANALYSIS (multi-region scope).
Next session instructions:
- Do not re-open the national analysis (archived RESULT B).
- Estimate the locked model exactly once on design_matrix_climate.csv:
  JSD ~ irr_share * mismatch_T + country FE, within-country bootstrap B=999
  seed 20261003. Then secondaries per 11_HYPOTHESIS_HIERARCHY.
- Report A-D outcome classes verbatim; rescue rules forbidden.
- Perennial hypothesis is underpowered (11 countries with variation) —
  report, do not re-tune.
