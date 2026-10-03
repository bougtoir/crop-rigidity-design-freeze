# 06 — Causal graph

## DAG (text form; directed edges A → B)

    Geography G (latitude, baseline climate, area)
      → Mismatch M        (drives exposure magnitude & footprint)
      → Legacy L          (history of specialization is geoclimatic)
      → Confounders       (baseline productivity, cropland share)
    Institutions/development D
      → L, → Transformation T (via capacity to reallocate), → M-reporting
    Baseline climate variability Vb
      → L (variability selects for diversified mixes)
      → T (variability experience may itself drive restructuring)
      → M (baseline variance scales standardized anomalies)
    L → T ?                    (main effect)
    M → T                      (main effect)
    L → (M × L) moderation → T (β3 target)
    Legacy-window rainfall/temp → M measurement (baseline niche)

## Covariate classification

See `06_COVARIATE_TABLE.csv` for the machine-readable version. Summary:

- **Confounders (include)**: latitude |absolute|, baseline climate variability
  (SD of annual growing-season T and P over 1961–1990), baseline cropland
  share, log country area, baseline GDP per capita (WB), baseline agricultural
  employment share (WB), baseline agricultural TFP proxy (yield level of
  dominant crop 1981–2000), region FE.
- **Mediators (exclude from primary; report in mediation-naïve sensitivity)**:
  contemporary trade openness, contemporary irrigation expansion, contemporary
  input use — all post-treatment w.r.t. legacy×mismatch.
- **Collider risks (never include)**: any variable defined on outcome-window
  crop shares (e.g. outcome-window diversification, crop income growth),
  selection into FAO reporting quality interacted with outcome.
- **Precision variables (optional, in extended spec)**: baseline population
  density, baseline yield volatility of dominant crop.
- **Not justified**: cultural-preference proxies, colonial-origin dummies,
  diet-composition indices — no defensible causal path that is not already
  proxied, and they invite storytelling.

## Identification caveats carried forward

- Mismatch is not randomized: specialization historically tracks climate
  (G→L and G→M). Latitude + baseline-variability + region FE partially close
  this; residual confounding is the principal limitation — documented in the
  risk register of the previous package and restated at the gate.
- M measured over the crop footprint → footprints differ by country;
  footprint size is controlled (log area) but within-country spatial
  reallocation of the same crop is an outcome too — flagged, not solved.
