# 05 — Climate-mismatch protocol (subnational)

## Construction

Same machinery as the completed national study, ported to admin-1:

- Baseline footprint: unit's dominant crop(s) at t0, MIRCA2000 condensed
  crop calendars for the unit's growing season (crop-specific by design).
- Climate: NASA POWER 0.5° monthly T2M/prec (1984–2020 on disk);
  SPEIbase 2.11 for the drought variant; growing-season aggregation via
  the established `seasonal()` code.
- Mismatch: Mahalanobis distance between baseline-regime climate
  (e.g. 1984–2001) and exposure-regime climate (2002–2020) in the
  crop's *seasonal* climate space, Ledoit–Wolf pooled covariance —
  identical form to the locked national measure, preserving
  cross-study interpretability. No post-treatment leakage (baseline
  niche estimated only on t0 window).
- GAEZ v4 suitability-change layer as the alternative mismatch metric
  (2010 vs 2070 scenario pairs already downloaded for wheat/cotton/
  sugarcane — limited crop set, usable for the subset).

## Anti-outcome-peeking rule

Metric chosen on coverage and agronomic interpretability only
(same pre-registered rule as national: crop-calendar dominant measure
primary, thermal-season rule and SPEI as robustness). Climate variables:
T2M + precip primary; heat extremes and SPEI as pre-declared variants.

## Unit-specific caveat

Admin-1 mismatch is noisier than national (smaller climate cells);
spatial smoothing of the climate field is required and must be frozen
before analysis (e.g. mismatch computed on the unit's own footprint
cells via MIRCA unit grid, already implemented for the national
exposure).
