# 08 Design-ready checklist (v3)

| # | item | status | evidence |
|---|---|---|---|
| 1 | per-unit level audit (source metadata + geometry) | DONE | `analysis/01_UNIT_LEVEL_AUDIT.csv`, `01_*.md` |
| 2 | one frozen subnational scale | DONE | admin-1 equiv {ADM1, HV admin-1, NUTS2}; `02_*.md` |
| 3 | no national observations in sample | DONE | NUTS0 bug fixed; 0 rows below first level |
| 4 | scale diagnostics (area, units/country, singletons) | DONE | `spatial_scale_diagnostics.csv`, `median_area_by_country.csv` |
| 5 | ≥2 eligible units per country | DONE | min 2, median 10.5 |
| 6 | duplicate geographies deduplicated | DONE | 20 dup rows removed, predeclared rule |
| 7 | canonical reproducible information sim | DONE | `information_simulation_v3.py` + byte-identical CSV check |
| 8 | outcome-blind DGP | DONE | marginal moments only; `04_*.md` class-B v2 exposure disclosed |
| 9 | exact null under b3=0 | DONE | induced interaction 1.27e-16 |
| 10 | effect grid, both signs | DONE | 0, ±0.15, ±0.30, ±0.50 |
| 11 | model family frozen (not by b3) | DONE | OLS + country FE; `03_*.md` |
| 12 | blocks rebuilt on final sample | DONE | `admin_spatial_blocks_v3.csv` |
| 13 | spatial type-I calibrated/classified | DONE | grid10 PASS 3.5–6.5% all rho |
| 14 | blindness audit | DONE | `04_BLINDNESS_AUDIT.md` |
| 15 | final sample info gate report | DONE | `07_*.md`; criteria not lowered |
| 16 | locked sample checksummed | DONE | `.sha256` |
| 17 | LOCK v3 yaml + hash | DONE | `SUBNATIONAL_PRIMARY_ANALYSIS_LOCK_v3.yaml` |
| 18 | real headline b3 not estimated/inspected | DONE | no such fit exists in repo (blindness audit) |
