# 05 — Temporal interval decision (frozen)

Adopted: **Interval D** — country/source-specific vintage pair within a frozen
gap range: baseline year nearest 2002 in [1998,2008], endline nearest 2019 in
[2013,2024], gap >= 8 years; endpoints smoothed over +/-1 year.

Rationale: A/B/C fixed windows would discard Brazil (2016) and most FAO
subnational countries (endline <=2019) while adding nothing for the dominant
HarvestStat/Eurostat blocks. Median realized gap = 17 y; pair distribution in
`analysis/design_matrix.csv`.
