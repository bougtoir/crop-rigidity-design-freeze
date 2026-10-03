# 08 — Irrigation exposure protocol (frozen)

Exposure I2 (primary): unit irrigated harvested-area share from SPAM 2010
zonal sums (sum of all `*_H_*_I.tif` / sum of `*_A.tif` within unit polygon,
clipped [0,1]). Same numerator/denominator family (harvested area, modelled
allocation of observed statistics).
I1 (US only, sensitivity): USDA Census reported `AG LAND, IRRIGATED - ACRES`
/ harvested acres (state level, DOMAIN=TOTAL).
I3 (GMIA area-equipped) not persisted in this build -> documented, not used.

Comparison (analysis/irrigation_source_comparison.csv):
- I1 US states mean 0.27 (sd 0.30); I2 coverage 353 units mean 0.088;
  cross-source correlation for the US overlap = 0.81 after clipping.
Alignment rule frozen: never mix area-equipped denominator with irrigated
harvested-area numerator.
