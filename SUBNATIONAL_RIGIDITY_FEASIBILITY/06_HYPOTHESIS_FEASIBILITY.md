# 06 — Hypothesis feasibility

| H | Statement | Estimand | Feasible at admin-1 | Assessment |
|---|---|---|---|---|
| H1 | mismatch × local specialization → less local switching | interaction of baseline unit HHI with mismatch on unit JSD | **yes** | Direct port of national model to ~1–3k units; cluster bootstrap at country/subregion level. Effect could be nonzero where national was null — that is the study's point, not guaranteed. |
| H2 | mismatch × baseline irrigation dependence → less transformation / delayed abandonment | same model with irrigation share; abandonment outcome variant | **yes** | GMIA v5 + SPAM `_I` split + MIRCA give three independent-ish exposure readings; physically interpretable — the strongest novelty claim. |
| H3 | mismatch effect differs annual vs perennial | interaction with perennial share; or crop-class-stratified mismatch | **yes** | Perennial share observable; crop-class mismatch computable from MIRCA classes. Gradient is literally the fixed-capital dose. |
| H4 | national flexibility via between-unit reallocation in high-legacy systems | decomposition T_c = W_c + B_c; B_c share vs country-mean fixed capital | **yes — and the most important** | Requires only the same admin stats; links new result to completed national null without touching it. |

## Estimation skeleton (for the eventual lock)

Unit-level fractional logit / beta regression of local JSD on
mismatch × each fixed-capital measure (separate models, no composite),
cluster bootstrap at country or M49 subregion (validated method already
exists), plus the H4 decomposition estimated per country with its own
bootstrap over units. Multiplicity: H1–H4 are one family — a single
pre-registered primary (recommend H2 irrigation as the physical-capital
flagship, H1 as the continuity spec, H3/H4 as co-primary descriptive).

## Feasibility caveat

Admin boundary harmonization across vintages is the binding constraint:
GSAP harmonizes via GADM but merging across ~2000–2020 requires a fixed
boundary base-year and a sliver/harmonization table. ~2 observed time
points is satisfied for many countries, but coverage is uneven (Africa
thinner). Pilot below confirms pipeline feasibility, not coverage
completeness — coverage audit is a required next-phase task.
