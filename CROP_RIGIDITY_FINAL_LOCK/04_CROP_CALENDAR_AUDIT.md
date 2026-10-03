# 04 — Crop-calendar audit and decision (Issue 4)

## Audit

| Candidate | Verdict |
|-----------|---------|
| **MIRCA2000 v1.1 condensed cropping calendars** | ADOPTED. Global (362 calendar units), crop-specific (26 classes), start/end months per sub-crop (up to 5 → double cropping preserved), circa-2000 vintage → temporally compatible with the baseline, already acquired under `data/raw/mirca/` |
| Sacks et al. global crop calendar | Coarser (single planting/harvest date per crop); MIRCA's monthly sub-crop structure dominates |
| GGCMI crop calendars | Derived largely from MIRCA/Sacks; no added value for baseline compatibility |

Implementation: `unit_code_grid` (5′ raster) maps every SPAM2000
footprint cell to its MIRCA calendar unit; rainfed + irrigated CCCs are
unioned; each footprint cell's growing months = union of its unit's
sub-crop seasons for the SPAM→MIRCA class(es) in
`CROP_CALENDAR_CROSSWALK.csv`.

## Comparison with the thermal rule (`analysis/calendar_vs_thermal_mismatch.csv`)

- Coverage: calendar 147 / thermal 148 finite of 183 estimation countries — equivalent.
- Pearson corr 0.930, Spearman 0.887; median |rank change| 10 (of ~147).
- Tropical (|lat|<23.5°, n=72): corr 0.964 — agreement strong where the thermal proxy is weakest.
- High-latitude (>55°, n=7): corr 0.80.

## DECISION (made without outcome association)

**Primary mismatch = MIRCA2000 crop-calendar-based Mahalanobis
mismatch** — climate exposure integrated only over the dominant crop's
actual baseline growing months. The >5 °C thermal rule is demoted to a
pre-registered robustness analysis and renamed **thermal-season
climatic displacement**.
