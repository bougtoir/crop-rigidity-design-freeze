# 02 Final sample report (V4, strict admin-1)

`analysis/PRIMARY_SUBNATIONAL_SAMPLE_LOCKED_V4.csv` (+ `.sha256`).

| quantity | V4 strict | V3 |
|---|---|---|
| units | **340** | 373 |
| countries | **23** | 28 |
| regions | **4** | 5 |
| grid10 blocks | 59 | 67 |
| median units/country | 11.0 | 10.5 |
| min units/country | 2 (Mauritania) | 2 |
| irr sd>0.01 within country | 21 / 23 | 25 / 28 |
| mismatch sd>0.01 within country | 22 / 23 | 27 / 28 |
| design condition number | 8.8 | 8.7 |

Region mix: SSA 233/18, N America 58/2, Asia 33/2 (IDN, PAK), Latin
America 16/1 (Brazil).

Removal: −33 NUTS2 statistical-region units (−5 European countries).
Nothing else changed — same missingness, same dedup, no JSD-based
selection.

Adequacy: 340 comparable first-level units, within-country variation in
21–22 countries, power preserved per the bounded information sim
(power ≥0.57 at |contrast|≥0.01–0.04 JSD units, ≥0.78 for the central
grid). Not collapsed below the minimum gate → continue.
