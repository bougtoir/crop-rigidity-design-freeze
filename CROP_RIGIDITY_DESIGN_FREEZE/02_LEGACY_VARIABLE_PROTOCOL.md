# 02 — Legacy variable protocol

## Forbidden

No weighted omnibus index. Legacy dependence is measured by separate,
preregisterable dimensions, each defined below with its own estimand column.

## Dimension A — crop-mix concentration (PRIMARY legacy variable)

**Primary measure: harvested-area HHI**, frozen before outcome modelling.

    HHI_i = Σ_c s_ic^2 ,  s_ic = mean harvested area of crop c in country i
    over the legacy window 1981–2000 / total harvested area over that window

Rationale for choosing HHI over entropy/top-1 before seeing outcome
associations:
- directly interpretable as portfolio concentration (an economic-biological
  concentration measure with a fixed 0–1 scale);
- robust to tail re-labelling of minor crops (unlike top-1 share, which jumps
  when the dominant crop changes identity);
- standard in trade/diversification literature → reviewer-legible.

Predefined robustness measures (frozen, not selected post hoc):
- Shannon entropy of s_ic (direction reversed: higher = less concentrated);
- top-1 share; top-3 share.

All four are computed by `scripts/02_design_diagnostics.py` and stored per
country in `analysis/design_diagnostics_summary.csv`.

## Dimension B — irrigation dependence (secondary legacy variable)

    IRR_i = irrigated harvested area / total harvested area, legacy window

Data: MIRCA2000 irrigated cropping calendars (acquired; baseline ~2000 —
flagged as time-mismatched, used only in sensitivity) + FAO AQUASTAT area
equipped for irrigation where required. Because MIRCA's reference year is
~2000 (end of legacy window, not centre), IRR is a *secondary* dimension and
is explicitly labelled as approximate-temporal in the covariate table.

## Dimension C — persistence / crop-mix inertia (sensitivity only)

    INERTIA_i = similarity (1 − JSD) between crop mix at t and t−20

**Mechanical-overlap guard**: this variable is *forbidden* in the primary
specification because the primary outcome IS mix change over a subsequent
window — a persistence measure computed on overlapping data mechanically
loads on the outcome. It is permitted only when the inertia window
(1961–1980) is fully disjoint from the outcome window (2001–2020) and legacy
concentration (1981–2000) lies strictly between them. Even then it is
sensitivity-only.

## Temporal ordering (frozen)

    inertia/sensitivity window   1961–1980
    legacy window                1981–2000   ← all primary predictors
    exposure window              2001–2020   ← climate mismatch
    outcome window               2001–2020   ← transformation vs legacy mix

No predictor may use information after 2000 in the primary specification.
Crop-mix aggregates exclude FAOSTAT aggregate items ("…Total", "…nes") so that
shares reflect single crops.
