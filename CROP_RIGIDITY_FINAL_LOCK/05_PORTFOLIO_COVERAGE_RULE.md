# 05 — Portfolio robustness coverage rule (Issue 5)

## Problem

Portfolio mismatch was share-weighted over crops with finite
mismatch; coverage fell to 0.0004–0.08 for some countries — a
"portfolio" of <1% of the legacy portfolio is not a portfolio.

## Rule (chosen a priori, before β3)

Portfolio mismatch may enter a robustness analysis only when

```
share_coverage_i = Σ_c s_ic over crops with finite mismatch  ≥ 0.70
```

- **≥ 0.70 is the frozen primary threshold** for portfolio robustness
  rows: a country's portfolio value is NA below it, never silently
  used.
- Sensitivity thresholds ≥0.50 / ≥0.80 are pre-registered; the
  threshold set was fixed from the coverage distribution alone
  (`analysis/portfolio_mismatch_v3.csv`, computed under the frozen
  1981–2001/2002–2020 ladder): median coverage 0.75; ≥0.5 → 151,
  ≥0.7 → 130, ≥0.8 → 100 of 229 valid-mix countries.

## Scope

- Applies to ALL portfolio-weighted robustness exposures (calendar- or
  thermal-based).
- The dominant-crop primary exposure is unaffected.
- Within the primary sample (N=147), countries below 0.70 coverage are
  dropped from portfolio robustness rows, counted in the analysis
  report's attrition table.
