# 01 — Unit of analysis decision

## Candidates

**DESIGN A — country × crop × year panel** (FAOSTAT QCL, 1961–2024, 169 crops,
254 reporting units, downloaded and verified).

**DESIGN B — grid × crop × time-window panel** (MapSPAM 5-arcmin geotiffs,
2005 v3.2 and 2010 v2.0 downloaded and verified readable).

## Comparison (assessed on acquired data)

| Criterion | Design A (country×crop×year) | Design B (grid×crop×window) |
|---|---|---|
| Sample size | ~210 countries × ~60 crops | ~2.2M grid cells × 42 crops — vastly larger nominal N |
| Measurement error | FAO-reported, heterogeneous reporting quality, but per-country multi-decade | model-allocated disaggregation; error structure opaque and correlated within country |
| Spatial dependence | moderate (country clusters) | extreme (spatial autocorrelation within countries/regions; effective N ≪ nominal N) |
| Climate exposure precision | country-level means only (NASA POWER/SPEI aggregates) | true grid-level climate join possible |
| Switching outcomes | yearly crop shares; genuine transformation observable 1961–2024 | only 2 usable epochs (2005, 2010); no transformation dynamics |
| Computational burden | trivial | heavy (per-cell mixes, raster pipelines) |
| Interpretability | policy-natural units | spatially precise but epoch-sparse |
| Global coverage | 210 countries after filtering | global cropland mask |
| Publication defensibility | standard in global agri-economics; robust SEs by country | the dominant objection — MapSPAM has ~1 effective cross-section per decade — cannot support a *transformation* outcome |

## Decision

**Primary design: DESIGN A — country × crop (mix) × period.**

Decisive reason: the estimand is *transformational flexibility over ~20-year
windows*, and only FAOSTAT provides a long annual crop-mix panel. MapSPAM's two
comparable epochs (2005, 2010) cannot measure transformation — they measure
levels. Using Design B would manufacture nominal N without temporal
information.

**Design B retained as sensitivity/validation**: MapSPAM 2005→2010 grid-level
mix change aggregated to ADM1/regions will validate that country-level JSD is
not an artefact of FAO reporting; MapSPAM also supplies the within-country
spatial distribution needed for climate-mismatch weighting.

## Consequence for temporal structure

Fixed pre-specified windows (no outcome-period look-ahead in predictors):

- legacy window: 1981–2000
- exposure window: 2001–2020
- outcome window: 2001–2020 (transformation relative to legacy mix)

Sensitivity windows: 1971–1990 / 1961–1980 legacy alternatives and 10-/30-yr
variants (frozen in `07_MULTIVERSE_PROTOCOL.csv`).

## Coverage actually available (measured, `analysis/design_diagnostics_*`)

- 210 countries with ≥10 reported years in both windows and ≥4 crops.
- Median 60 distinct crops per country.
- Legacy HHI median 0.138 (p10 0.083, p90 0.256) — wide dispersion, no
  degenerate concentration at the boundaries.
- Transformation JSD median 0.126 (p10 0.078, p90 0.213); dominant-crop
  replacement in 12.9% of countries.
