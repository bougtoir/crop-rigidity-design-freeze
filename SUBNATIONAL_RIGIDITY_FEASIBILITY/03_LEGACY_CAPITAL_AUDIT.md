# 03 — Fixed-capital exposure audit

Mandate: separate variables, no composite index; at least one physically
interpretable fixed-capital measure beyond HHI.

| # | Variable | Construction | Status |
|---|---|---|---|
| A | **Irrigation dependence** | irrigated harvested area / total harvested area, baseline vintage. Sources: SPAM `_I` technology split (pixel), MIRCA2000 irrigated areas, GMIA v5 (area equipped for irrigation, ~2005, incl. groundwater/surface split) | **directly observed (admin via census share) / modelled (pixel)** — physically interpretable, primary candidate |
| B | Local crop concentration | HHI or dominant-crop share of baseline harvested-area mix within the unit | directly observed (admin stats); continuous with national study |
| C | **Perennial crop share** | share of harvested area in perennial classes (orchard/vine/plantation: oil palm, cocoa, coffee, citrus, grapes, date, bananas→perennial-coded) at baseline; MIRCA perennial classes; EarthStat physio-type layer (annuals/perennials) | **directly observed** — physically interpretable switching-cost gradient, primary candidate |
| D | Persistence of crop geography | overlap/JSD between the two earliest available vintages (e.g. MRF-2000 vs SPAM2005) of within-unit crop mix | computable but **proxy** — low persistence could be measurement noise (see unit decision); usable at admin level only |
| E | Water-infrastructure dependence | GMIA v5 area-equipped + groundwater share; distance to large dams (GRanD) | partially observed (GMIA stat-based, GRanD inventory) — proxy |
| F | Distance to processing/storage | no credible global layer (some regional mapping only) | **unavailable** at required quality |

## Selection logic (no outcome peeking)

A and C satisfy the Nature-level requirement for physically interpretable
fixed capital: irrigation share is literal sunk water infrastructure;
perennial share is literal multi-decadal biological capital. B is the
direct subnational analogue of the (null) national HHI exposure — needed
to attribute a positive subnational result to *capital* rather than to
*portfolio specialization per se*. D and E are secondary; F dropped.

Recommended primary exposure pair for H1–H3: **irrigation-dependence (A)
and perennial share (C)**, with B as the specialization control — the
comparison B vs A/C is exactly the design's discriminating content
("fixed capital, not specialization per se").
