# 02 — Unit-of-analysis decision

## Audit summary (see 02_SPATIAL_DATA_AUDIT.csv)

Critical constraint surfaced: **no global pixel-level crop dataset has two
independent, methodologically comparable vintages.** SPAM vintages share
priors/suitability inputs and were revised between releases; CROPGRIDS is
explicitly seeded by MRF/EarthStat 2000. Pixel-level "change" between
modelled vintages mixes real change with model revision — measured in the
pilot (below) and confirmed by the SPAM sensitivity literature.

Real repeated observations exist at **admin-1/admin-2** level (GSAP,
Agro-MAPS, FAO subnational stats) and in the input statistics behind
every SPAM release (now openly distributed with SPAM2020).

## Comparison of candidate units

| Unit | baseline obs | repeated obs | N | spatial dependence | transformation measurable | verdict |
|---|---|---|---|---|---|---|
| 5′ / 10 km pixel | SPAM/MRF vintages | modelled, non-independent | huge | extreme | apparent, but confounded by model revision | **Rejected as primary** — cannot separate real change from method change |
| 0.5° block | aggregated SPAM/GSAP | same caveat, damped | ~10k | high | partial | usable only as sensitivity layer |
| **admin-1 (harmonized)** | GSAP/Agro-MAPS/SPAM inputs | observed multi-vintage | ~1–3k cultivated units | moderate (cluster inference available) | yes — real statistics | **PRIMARY UNIT** |
| agro-ecological zone | derivable | same as inputs | ~200 | low-mod | coarse | exploratory only |
| crop-specific production cells | MIRCA/SPAM | modelled | variable | high | no (not independent) | rejected |

## Decision

**Primary unit: harmonized admin-1** (admin-2 where GSAP coverage allows;
GADM-coded). This trades N for observational validity — the preferred
requirement (≥2 observed time points with comparable methodology) is met
only at the admin level, where the underlying census statistics — not
modelled allocations — are the data.

SPAM pixel products retain a defined role: (a) fixed-capital *baseline*
layers (irrigated-area fraction via SPAM `_I` technology split, MIRCA,
GMIA v5; perennial share), measured once at baseline — single-vintage
modelled exposures are acceptable because they are not differenced;
(b) sensitivity decomposition of within- vs between-location change.

## Pilot corroboration (08_PILOT_REPORT.md)

SPAM2005→2010 pixel correlation for wheat is 0.84 with 14% of cultivated
cells showing "disappearance"; aggregating to 0.5°/1.5°/2.5° blocks
recovers correlations 0.96/0.98/0.99 and halves the apparent churn —
consistent with model-level allocation noise dominating below ~0.5°.
Admin-level analysis is the defensible scale.
