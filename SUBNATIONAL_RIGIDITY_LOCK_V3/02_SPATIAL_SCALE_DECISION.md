# 02 Spatial scale decision

## Frozen scale: first subnational administrative level ("admin-1")

The single primary scale is the **first administrative level below the
nation state**, operationally:

| source family | accepted level | mapping |
|---|---|---|
| GADM 4.1 | `ADM1` | direct |
| HarvestStat (Africa) | `admin_1` | direct |
| Eurostat | `NUTS2` only | the NUTS level that is most uniformly first-level-subdividing across contributing countries; NUTS1 countries and NUTS0 countries are excluded, not mixed |
| USDA Census | state | direct (county data aggregated to state in v2) |
| StatCan / IBGE | province / UF | direct |

Rationale: "true admin-1" is the highest-priority option in the audit
spec. A single predeclared NUTS level could not cover the
GADM/HarvestStat countries, so the common target scale is the
administrative level itself, not a grid or a statistical convenience.
NUTS1 and NUTS2 are **not** mixed: contributing Eurostat countries enter
only through NUTS2 rows, and countries whose Eurostat coverage exists
only at NUTS0/NUTS1 are excluded from the primary sample (sensitivity
only).

## Europe: NUTS ↔ admin-1 mapping

Eurostat `apro_cpshr` rows at NUTS2 are used for EL, IE, PT, HR, CH
(Switzerland reports at NUTS2 districts/statistical regions). For
Germany/Belgium/UK the first-level units are NUTS1 — those countries have
no eligible unit at the frozen level and are excluded (in v2 they were
silently present as NUTS0 rows; removed). Old codes (EL11–EL25, IE01/02)
are mapped through the NUTS-2010/2013 vintages in which the statistics
were reported; geometry falls back 2021 → 2016 → 2010 vintage.

## Scale diagnostics (see analysis/spatial_scale_diagnostics.csv)

* Area distribution across the 373 locked units is wide but subnational:
  all units are first-level admin regions (median area ~tens of thousands
  km²; see `median_area_by_country.csv`).
* ≥2 eligible units per country required (prefer ≥3 where feasible);
  median 10.5 units/country, minimum 2 (IE, Mauritania, HR).
* Countries contributing a single unit are excluded — country fixed
  effects cannot identify local rigidity from one local observation.

## Excluded-scale inventory (for transparency)

* 44 rows at NUTS0/NUTS1/HV2/other levels dropped.
* Countries removed entirely for lacking admin-1 coverage: the
  NUTS0-only Eurostat set (CY, LU, EE, MT, ME and the v2-phantom
  DE/BE/FR/IT/PL/NL/CZ/SE/RO/BG/BA/RS/XK rows that were really
  country-level), Slovenia (exposure gaps), and all single-unit
  leftovers.
