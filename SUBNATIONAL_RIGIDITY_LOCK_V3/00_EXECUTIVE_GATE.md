# 00 Executive gate — SUBNATIONAL RIGIDITY, LOCK V3

**DECISION: GO TO SUBNATIONAL PRIMARY ANALYSIS (multi-region scope)**

The two blocking problems found in the independent audit are resolved:

1. **Spatial unit harmonization.** Every primary unit is now a genuinely
   comparable local unit: GADM admin-1, HarvestStat admin-1, or Eurostat
   NUTS2. No national (NUTS0) observations remain in the primary sample;
   the `admin_level = f(strlen)` bug that smuggled 2-character NUTS0 codes
   into the design matrix is fixed, and duplicate geographies (same
   `gadm41_gid` covered by two sources) are deduplicated by a predeclared,
   outcome-blind rule.
2. **Outcome-blind, exactly reproducible information simulation.** The v2
   simulation used observed unit-level JSD as its DGP baseline (class-B
   exposure). The v3 DGP uses only marginal moments (mean 0.13, SD 0.09
   on the JSD support), an explicitly assigned interaction, and an
   analytically exact null (induced interaction = 1.3e-16 under b3=0).
   `information_simulation_v3.py` reproduces its CSV byte-identically.

## Final sample

**373 admin-1-equivalent units / 28 countries / 5 regions**
(SSA 233/18, Europe 33/5, Northern America 58/2, Latin America 16/1,
Asia 33/2). Median 10.5 units/country, minimum 2. All units carry
pre-outcome baseline irrigation (SPAM2000 zonal), MIRCA-calendar mismatch,
and a comparable JSD outcome.

## Gate conditions (all pass)

| # | condition | status |
|---|-----------|--------|
| 1 | every unit at frozen subnational level | PASS (GADM ADM1 / HV admin-1 / NUTS2 only) |
| 2 | no country-level observations | PASS (NUTS0 bug fixed; 0 national rows) |
| 3 | solo-unit countries excluded | PASS (min 2/country; SI dropped) |
| 4 | blocks rebuilt on final sample | PASS (67 grid10 / 49 grid15 / 75 km blocks) |
| 5 | information simulation outcome-blind | PASS (marginal moments only) |
| 6 | b3=0 → true null interaction | PASS (induced = 1.3e-16 < 1e-8) |
| 7 | sim script reproduces CSV | PASS (byte-identical rerun, package_validation.py) |
| 8 | primary model family frozen | PASS (OLS + country FE, see 03) |
| 9 | spatial type-I calibrated or classified | PASS (grid10 type-I 3.5–6.5%, all scenarios PASS) |
| 10 | blindness audit complete | PASS (04_BLINDNESS_AUDIT.md; v2 exposure disclosed) |
| 11 | sample + lock checksummed | PASS (PRIMARY_SUBNATIONAL_SAMPLE_LOCKED.sha256, LOCK_v3.sha256) |
| 12 | no result-driven redesign | PASS (real b3 never estimated; national result untouched) |

## What changed vs v2

* Strict level audit → sample shrank 369 → 373 units but from 38 → 28
  countries (10 NUTS0-only or single-unit countries excluded; Burkina
  Faso and Ireland recovered after geometry/name fixes).
* Exposure repairs: duplicate-geometry dedup restored lost irrigation
  values; MIRCA unit-name parser fixed (trailing-tab rows silently
  dropped 'Burkina Faso', 'Greece', 'Ireland', 'Portugal' calendars);
  NUTS2010/2016 geometry fallback for pre-2021 unit codes; 11 POWER
  centroid fetches added for newly geometric units.
* Inference: grid10 block bootstrap recalibrated on the final sample —
  type-I 3.5–6.5% across rho = 1/150/500/1500 km. Country CRVE remains
  anti-conservative (16–20.5%) and stays excluded.
* Empirical scope label: **multi-region** (SSA-dominant), unchanged.

The national primary result (RESULT B: b3 = +0.0046 [-0.131, +0.143])
is untouched; this subnational analysis is the prespecified follow-up.
The real subnational b3 has NOT been estimated at any point.
