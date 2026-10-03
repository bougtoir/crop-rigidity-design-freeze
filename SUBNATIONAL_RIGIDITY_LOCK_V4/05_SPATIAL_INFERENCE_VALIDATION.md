# 05 Spatial inference validation (v4, bounded DGP)

Blocks rebuilt on the strict 340-unit sample
(`analysis/admin_spatial_blocks_v4.csv`); type-I under the bounded
fractional-logit/Beta DGP at latent b3=0, 200 reps per rho scenario.

| scheme | n blocks | med units | singletons | crossing countries |
|---|---|---|---|---|
| grid10 (primary) | 59 | 4 | 18 | 15 |
| grid15 | 43 | 4 | 8 | 16 |
| kmeans | 67 | 5 | 3 | 0 |

| scenario | HC3 | CRVE | grid10 | grid15 | kmeans |
|---|---|---|---|---|---|
| rho=1km | .055 P | .155 F | .045 P | .035 P | .025 P |
| rho=150 | .070 P | .150 F | .035 P | .020 P | .020 P |
| rho=500 | .040 P | .195 F | .035 P | .025 P | .045 P |
| rho=1500 | .070 P | .195 F | .030 P | .030 P | .045 P |

grid10 block bootstrap: **PASS in all scenarios** (type-I 3.0–4.5%,
coverage 95.5–97.0%) → frozen primary. Country CRVE FAILS (15–19.5%)
and is excluded; HC3 passable but non-spatial, benchmark only.
