# 04 — Transformational-flexibility outcome protocol

## Primary outcome (frozen, continuous)

**Jensen–Shannon distance between legacy-window and outcome-window crop-mix
distributions**:

    TRANSFORM_i = JSD( p_i , q_i )

where p_i = crop shares on harvested area, mean over 1981–2000, and
q_i = shares over 2001–2020. Shares exclude FAOSTAT aggregate items.

Measured (analysis/design_diagnostics_summary.csv): median 0.126,
IQR ~0.08–0.21, range 0.015–0.60 over 210 countries — sufficient continuous
variation to regress, and bounded so fractional/beta models are admissible.

## Secondary outcome (frozen, binary)

**Dominant-crop replacement**: 1 if argmax_c s_ic differs between the legacy
and outcome windows, else 0. Observed prevalence 12.9% (27/210 countries) —
logistic model viable but low-information; flagged as low-power secondary.

## Additional predefined secondary outcomes (not primary)

- ΔHHI_i = HHI(outcome window) − HHI(legacy window) — median −0.009, range
  −0.16 to +0.28;
- emergence of a previously minor crop (share <2% → >10%): observed only 1%
  of countries — recorded but deemed too rare for a standalone estimand;
- spatial crop-migration centroid displacement: requires MapSPAM two-epoch
  processing; reserved for the Design-B validation arm.

## Explicitly excluded

- **Yield retention / yield resilience is NOT a transformation outcome**
  (productivity stability measures adaptiveness of a fixed mix, not
  transformational flexibility). It may appear only as a clearly-labelled
  secondary resilience descriptor.
- Area *level* changes (total cropland expansion) are confounders, not
  outcomes.

## Mechanical-overlap check

Outcome uses shares in disjoint windows from all primary predictors; legacy
HHI/entropy/top-k are computed on 1981–2000 only. No variable on the right
hand side contains outcome-window crop shares. The persistence dimension is
excluded from the primary model for exactly this reason (see
02_LEGACY_VARIABLE_PROTOCOL.md, Dimension C).
