# 01 Geographic scale — final (strict)

## Frozen strict primary scale

Only documented first-level administrative units:

* GADM ADM1 (Indonesia, Pakistan, Burkina Faso residual rows)
* HarvestStat `admin_1` (Sub-Saharan Africa)
* US states, Canadian provinces, Brazilian UFs

## Eurostat verdict (see 01_EUROPE_ADMIN_EQUIVALENCE.csv)

| country | NUTS level | actual first level | equivalent? |
|---|---|---|---|
| CH | NUTS2 grossregionen | cantons (NUTS3) | NO |
| EL | NUTS2 (old codes) | 13 periphereies (NUTS3) | NO |
| HR | NUTS2 statistical regions | 21 zupanije (NUTS3) | NO |
| IE | NUTS2 IE01/IE02 | counties | NO |
| PT | NUTS2 regioes | districts (NUTS3) | NO |

All five countries' NUTS2 rows are statistical aggregates of smaller
first-level units; none is a documented one-to-one equivalent. They are
excluded from primary and held as a prespecified **NUTS2 sensitivity
set** (not discarded): the sensitivity run will later compare estimates
with/without them, without touching primary geography.

Consequence: Europe exits the primary sample — a data-availability
limitation, not a scale compromise. Scope label remains *multi-region*.
