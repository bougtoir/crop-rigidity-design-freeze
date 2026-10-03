# 01 BASELINE IRRIGATION SOURCE AUDIT

Requirement: pre-outcome (≤~2002) fixed-capital exposure — irrigated
harvested area / total harvested area, admin-1 resolution.

## Candidates evaluated (see analysis/baseline_irrigation_source_comparison.csv)

| Source | Ref period | Observed/modelled | Numerator | Denominator | Resolution | Coverage in sample | License | Assessment |
|---|---|---|---|---|---|---|---|---|
| **SPAM2000 v3.0.7** | ~2000 | modelled (cross-entropy allocation of subnat stats) | irrigated harvested area per crop (_I) | total harvested area (_A) | 5 arc-min raster | 384/427 units; 369/369 of final sample | CC BY 4.0 | **PRIMARY** — same pipeline as SPAM2010 but precedes the transformation window |
| MIRCA2000 CCC | ~2000 | modelled | irrigated harvested area (CCC area fields) | rainfed+irrigated area | MIRCA spatial units (country or admin-1) | 362 units | free research use | Fallback/validation; coarser resolution (country-level for most countries → zero within-country variance), rank-corr with SPAM2010 only 0.45 |
| USDA Census reported irrigation | 2002 | observed (census) | reported irrigated acres | harvested cropland acres | state | 50 units | public | US-only robustness; construct differs (acres not harvested share) |
| SPAM2010 v2.0 | ~2010 | modelled | same as SPAM2000 | same | 5 arc-min | 353 units | CC BY 4.0 | **REJECTED as primary**: inside baseline→endline window (temporal leakage). Retained as predefined robustness |
| GMIA v5 | ~2005 | observed-modelled | area equipped for irrigation | — | 5 arc-min | — | free | Demoted: post-2002 and denominator mismatch ("area equipped" ≠ irrigated harvested area; not silently equated) |

## Outcome-free comparison vs SPAM2010

- SPAM2000 vs SPAM2010 (n=353): corr 0.79, MAD 0.063, rank 0.65
- MIRCA2000 vs SPAM2010 (n=353): corr 0.76, MAD 0.056, rank 0.45
- Largest 2000-vs-2010 disagreement: PT, Pakistan, Indonesia, Sudan, EL,
  FR (irrigation expansion 2000→2010; direction consistent with real
  growth, not artefact)
- USDA reported (mean 0.27) systematically above zonal estimates
  (construct: acres basis); documented disagreement, corr 0.81 vs SPAM2010

## Decision support

SPAM2000 chosen on **measurement validity + temporal ordering only**
(year 2000 precedes every country's endline; identical construct to the
demoted SPAM2010; highest admin-1 coverage; US reported values corr 0.8
validates the zonal method). No JSD association was examined.
