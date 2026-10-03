# 02 — Boundary harmonization protocol (frozen)

Reference geometry: **GADM 4.1 admin-1** (gadm_410-levels.gpkg, 3,662 units) is the
canonical reporting frame. Each source's own stable identifier is retained as the
primary unit key; units are mapped to GADM4.1 GID_1 where a name/code match exists.

## Classification (ADMIN_BOUNDARY_CROSSWALK.csv)
- `unchanged` — unit identifier stable across vintages within its source
  (HarvestStat fnid -> admin-1 label; FAO GADM_CODE; NUTS codes present both
  sides of revisions; FIPS/UF/province codes).
- `unresolved` — NUTS code retired/introduced at the 2013/2016 revisions
  (107 units). These are excluded from the analysis set.
- Match to GADM4.1: 575/1,218 units name/code-matched; the remainder keep
  source-native stable boundaries (documented; no spatial pooling).

## Aggregation rules (frozen)
1. Prefer the coarsest stable geography per country (admin-1).
2. When child-level data exist but parents differ (HarvestStat admin-2 fnids),
   aggregate by simple area-weighted sum of harvested areas.
3. Never interpolate across boundary changes.
4. Units failing the cross-vintage identity test are dropped (unresolved).
N sensitivity: dropping the 107 unresolved NUTS units and all name-mismatched
units changes N from 1,218 -> 461 after temporal rules; see coverage report.
