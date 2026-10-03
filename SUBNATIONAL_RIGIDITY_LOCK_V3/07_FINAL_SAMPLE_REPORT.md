# 07 Final sample and information gate report

Locked file: `analysis/PRIMARY_SUBNATIONAL_SAMPLE_LOCKED.csv`
(SHA-256 in `.sha256`; unit IDs frozen in LOCK_v3.yaml).

## Composition

| quantity | value |
|---|---|
| admin units | **373** |
| countries | **28** |
| world regions | **5** (SSA 233u/18c, Europe 33/5, N America 58/2, Latin America 16/1, Asia 33/2) |
| geographic blocks (grid10) | 67 |
| median units/country | 10.5 |
| minimum units/country | 2 (IE, Mauritania, HR) |
| agricultural-area coverage | 100% of units have SPAM2000 harvested-area sums (`spam_A_ha` > 0) |
| JSD mean / sd | 0.274 / 0.177 |

## Within-country variation (identification basis)

* irrigation sd > 0.01 within country: **25 of 28 countries**
* mismatch sd > 0.01 within country: **27 of 28**
* corr(irrigation, mismatch) overall: +0.05 → interaction identified
* standardized-design condition number: **8.7** (no collinearity concern)

## Attrition (`analysis/sample_attrition_v3.csv`)

| stage | units | countries | dropped | reason |
|---|---|---|---|---|
| v2 matrix | 461 | 51 | — | starting pool |
| eligible level | 409 | 29 | 52 | non-admin-1 + solo-country units |
| dedup shared gadm41_gid | 389 | 29 | 20 | same physical region, kept richer source |
| complete exposures | 374 | 29 | 15 | missing irr_share_base2000 / mismatch_T (e.g. GADM:IDN.15_1 no polygon; Slovenia) |
| ≥2 units/country | **373** | **28** | 1 | final lock |

## Judgment against the "too small" criterion

The sample is *not* declared too small: 373 comparable local units across
28 countries and 5 regions, within-country predictor variation in 25–27
countries, and calibrated power 1.0 at |b3| ≥ 0.15. This exceeds the
information basis on which the earlier multi-region GO was issued
(design-freeze sims ran on N ≈ 335/24 countries) and meets every
minimum-criteria item without relaxing any rule. No heterogeneous scale
was reintroduced to reach this size.
