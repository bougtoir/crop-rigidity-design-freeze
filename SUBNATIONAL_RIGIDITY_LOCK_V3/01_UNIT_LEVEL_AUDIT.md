# 01 Unit-level audit

Per-unit audit of all 461 rows in the v2 primary design matrix.
CSV: `analysis/01_UNIT_LEVEL_AUDIT.csv`
(`unit_id, country, source, source_native_level, source_native_level_name,
reference_admin_level, reference_geometry_id, parent_country, area_km2,
has_geometry, harmonization_status`).

## Method

Levels were assigned from **source metadata and geometry hierarchy**, not
string length:

* `GADM:` and `US:`/`BR:`/`CA:` units → GADM 4.1 ADM_1 (or the country-specific
  first-level equivalent: US states, Brazilian UFs, Canadian provinces).
* `HV1:` → HarvestStat `admin_1` field (humanitarian first-level units).
* `HV2:` → HarvestStat `fnid` (second-level) — **not** admin-1; 0 such rows
  reached the design matrix anyway.
* bare NUTS ids → level from the code list the id appears in (2021 file
  first, then 2016, then 2010 vintage): 2 chars = NUTS0, 3 = NUTS1,
  4 = NUTS2. This replaces the v2 `len==4 → level 2` shortcut that had
  admitted 2-character NUTS0 codes as "level 1".

## Result

| harmonization_status | units |
|---|---|
| eligible (admin-1 / humanitarian admin-1 / NUTS2) | 409 |
| excluded_level (NUTS0 country rows, NUTS1 where not first level) | 44 |
| excluded_solo_country (eligible level but sole unit in country) | 8 |
| **total** | **461** |

Eligible levels frozen: `{ADM1, humanitarian admin1, NUTS2}`. These three
are harmonized onto the common target scale "first subnational
administrative level" (see 02_SPATIAL_SCALE_DECISION.md).

## Findings

* The v2 sample mixed NUTS0 (e.g. country-level Eurostat rows), NUTS1,
  NUTS2, GADM ADM1 and humanitarian admin-1/admin-2. 44 rows failed the
  level rule.
* Duplicate physical regions existed: HarvestStat and FAO/GADM rows share
  the same `gadm41_gid` for Burkina Faso (13), Ethiopia (8), Senegal,
  Cameroon, Zimbabwe. Resolved by a predeclared dedup rule (keep the
  source contributing more units in the country; tie → HV1).
* Geographic repair (outcome-blind): the shared zone raster had
  overwritten duplicate polygons, silently voiding SPAM2000 zonal sums;
  MIRCA `unit_name.txt` rows with trailing tabs were dropped by the
  parser, removing the national calendars of Burkina Faso, Greece,
  Ireland, Portugal; EL11/IE01-style codes needed NUTS-2010-vintage
  geometry. Fixes restored Burkina Faso (14 units) and Ireland (2).
* Unrecoverable: `GADM:IDN.15_1` (no GADM-4.1 polygon for that code);
  Slovenia's 2 eligible units lacked complete exposures → country dropped.
