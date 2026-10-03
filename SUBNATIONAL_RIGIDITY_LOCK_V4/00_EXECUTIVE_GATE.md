# 00 Executive gate — SUBNATIONAL RIGIDITY, LOCK V4

**DECISION: GO TO SUBNATIONAL PRIMARY ANALYSIS (multi-region scope)**

The audit's two remaining defects are repaired; nothing else was
redesigned:

1. **NUTS2 is not universally admin-1.** Every Eurostat NUTS2 unit in
   the sample (EL, IE, PT, CH, HR — 33 units / 5 countries) is a
   statistical region, not the country's first administrative level
   (`01_EUROPE_ADMIN_EQUIVALENCE.csv` documents each). They are removed
   from the strict primary sample and retained only as a prespecified
   NUTS2 sensitivity set.
2. **Bounded information simulation.** The DGP is now
   fractional-logit/Beta — bounded in [0,1] by construction, calibrated
   to the V4 marginal JSD (mean 0.293, SD 0.173) using only marginal
   moments, with an exactly-zero generating-scale interaction under
   b3=0 and an interpretable JSD-scale effect grid (0, ±0.01, ±0.02,
   ±0.04).

## Strict primary sample

**340 units / 23 countries / 4 regions** (Sub-Saharan Africa 233u/18c,
Northern America 58/2, Asia 33/2, Latin America 16/1). Every unit is a
documented first-level administrative unit: GADM ADM1, HarvestStat
admin_1, US state, Canadian province, Brazilian UF. Median 11
units/country, minimum 2.

## Gate conditions (all pass)

| # | condition | status |
|---|-----------|--------|
| 1 | only true first-level units | PASS (NUTS2 non-equivalents removed) |
| 2 | NUTS2 non-equivalents outside primary | PASS (sensitivity set only) |
| 3 | sample adequate | PASS (340/23/4 regions; variation in 21–22 countries) |
| 4 | bounded synth outcomes match marginal JSD | PASS (0.2895/0.1743 vs 0.2932/0.1732) |
| 5 | no unit-level JSD in DGP | PASS |
| 6 | true null exactly zero | PASS (latent 0.0; JSD projection −0.0046 ≪ se) |
| 7 | OLS + bootstrap acceptable under bounded DGP | PASS (type-I 5.0%, coverage 95.5%) |
| 8 | blocks rebuilt on V4 | PASS (59/43/67 blocks) |
| 9 | outputs reproducible | PASS (byte-identical, package_validation_v4) |
| 10 | blindness intact | PASS (no real b3 fit exists — 06 recheck) |
| 11 | V4 sample + lock checksummed | PASS |

Real subnational β3 remains unestimated.
