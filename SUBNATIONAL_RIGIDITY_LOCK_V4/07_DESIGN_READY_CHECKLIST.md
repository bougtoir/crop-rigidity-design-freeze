# 07 Design-ready checklist (v4)

| # | item | status |
|---|---|---|
| 1 | strict first-level geography | DONE — NUTS2 non-equivalents removed |
| 2 | Europe equivalence table | DONE — `01_EUROPE_ADMIN_EQUIVALENCE.csv` (all NO) |
| 3 | NUTS2 sensitivity defined | DONE — excluded units kept as sensitivity set |
| 4 | V4 sample + sha256 | DONE — 340/23 |
| 5 | marginal JSD summary (no unit-level use) | DONE — `jsd_marginal_summary_v4.csv` |
| 6 | bounded DGP (fractional logit + Beta) | DONE — support [0,1] by construction |
| 7 | calibration to marginal mean/SD only | DONE — alpha −1.05, phi 30 |
| 8 | exact null | DONE — latent 0; projection −0.0046 reported |
| 9 | effect grid in JSD contrasts | DONE — 0, ±0.01, ±0.02, ±0.04 |
| 10 | OLS retained on bounded-DGP behaviour | DONE — type-I 5%, cov 95.5% |
| 11 | blocks rebuilt + type-I on V4 | DONE — grid10 PASS all rho |
| 12 | reproducible scripts | DONE — byte-identical + package_validation_v4 |
| 13 | blindness recheck | DONE — class A |
| 14 | V4 lock yaml + sha256 | DONE |
| 15 | real β3 untouched | DONE |
