# 01 — Primary sample flow (Issue 1)

The frozen PRIMARY exposure is the **dominant-crop MIRCA2000
crop-calendar Mahalanobis mismatch** under the 2002-boundary ladder
(`analysis/mismatch_diagnostics_v3.csv`, column
`mismatch_calendar`). All power/information work now uses exactly this
sample — no portfolio-only countries, corrected taxonomy HHI/JSD,
UN M49 mapping.

## Attrition (`01_PRIMARY_SAMPLE_FLOW.csv`)

| stage | n |
|-------|---|
| initial countries (valid crop-mix data: ≥10yrs each window, ≥4 crops) | 229 |
| valid HHI (finite) | 229 |
| valid JSD (finite) | 229 |
| valid ISO3/country mapping | 183 |
| valid dominant-crop SPAM class | 183 |
| valid dominant calendar mismatch (finite) | 147 |
| valid region/subregion | 147 |
| **FINAL primary N** | **147** |

Region coverage: 5 M49 regions, 20 subregions. Largest losses: 46
valid-mix entities are FAO aggregates/historical entities excluded by
name (not reassigned); 36 mapped countries lack a finite dominant-crop
calendar mismatch (no SPAM2000 footprint cells for the dominant class,
no POWER coverage, or <10 seasonal observations).

`analysis/primary_sample_preoutcome.csv` carries the frozen sample:
iso3, country, dominant_crop, spam_crop, hhi, jsd, mismatch, region,
subregion, footprint centroid (used for spatial inference).
