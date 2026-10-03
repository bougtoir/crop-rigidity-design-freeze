# 01 — Primary Mismatch Construction (real data)

## Pipeline (the audited 7 steps)

1. **Dominant crop** per country: largest harvested-area share over the
   legacy window 1981–2000, on the post-audit FAOSTAT item set
   (`FAOSTAT_CROP_ITEM_AUDIT.csv`); mapped to a SPAM2000 class via
   `SPAM_FAOSTAT_CROSSWALK.csv`. No crop is silently dropped.
2. **Footprint**: SPAM2000 per-pixel harvested area (`spam_h.csv`,
   dbf-csv release of v3.0.7), pixels with area > 0, assigned to
   countries by `stat_code` (ISO3; FIPS province prefixes mapped to
   ISO3 via an explicit, documented table).
3. **Climate cells**: footprint pixels binned to the NASA POWER grid
   (0.5° lat × 0.625° lon); per-cell monthly T2M and PRECTOTCORR fetched
   for every occupied cell (regional API, chunked to legal bboxes).
4. **Growing season**: per cell, months whose baseline climatological
   mean T2M > 5 °C — a thermal rule that needs no crop-calendar input.
5. **Seasonal vectors**: per cell × year, growing-season mean T2M and
   total PRECTOTCORR → (T, P) pairs.
6. **Baseline vs exposure**: baseline 1984–2000, exposure 2001–2020
   (POWER coverage constraint documented in `00_...`).
7. **Mahalanobis distance**: D = sqrt((μ_e − μ_b)′ Σ_b⁻¹ (μ_e − μ_b)),
   Σ_b = Ledoit–Wolf-shrunk baseline covariance — one common
   regularization rule for all countries, no per-country tuning.

## Diagnostics (analysis/mismatch_diagnostics.csv)

- **Coverage**: 130 of 164 mappable estimation countries have a
  non-missing mismatch. Missingness is concentrated in small island
  states without SPAM2000 footprint pixels or POWER coverage —
  reported, not silently dropped.
- **Occupied POWER cells per country**: median 75, IQR 28–181, max 1952.
- **Baseline covariance condition number**: median ~34, max ~434 — all
  well within invertible range.
- **Shrinkage**: Ledoit–Wolf intensity is estimated per country under
  the same rule; the few full-shrink cases (intensity 1.0) are
  single/double-cell footprints where the rule — not an ad-hoc fix —
  stabilizes the covariance. Flagged in the diagnostics file (`reg`
  column).
- **Missing T/P fraction**: 0.0 in every country (NASA POWER monthly
  series are complete over footprint cells).
- **Mismatch magnitudes**: median 0.48 SD units, IQR 0.29–0.73, max 2.25.

## Stability statement

Covariance estimation is stable under the common regularization rule
(condition numbers ≲ 500, determinants bounded away from numerical
singularity except for degenerate 1–2 cell footprints which are
recorded). No country-specific covariance fix was applied. The exposure
variable produced is `analysis/primary_mismatch_country.csv`
(dominant-crop mismatch per country).
