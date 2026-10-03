# 01 — Admin crop data coverage report (actual usable coverage)

Computed from `analysis/admin_crop_observation_matrix.parquet` (437,923 unit-crop-year
rows; 1,218 admin-1 units; 80 countries; 6 acquired sources).

## Usable coverage (units with >=2 vintages observed)
- Units: 1,782 unit-coverage records; 1,218 distinct admin-1 units; 80 countries.
- After temporal-pair filtering (baseline in [1998,2008], endline in [2013,2024],
  gap >= 8y, >=3 canonical crop categories each vintage): **461 units, 51 countries**
  (design_matrix.csv).
- Regions covered: Africa 21 countries / 261 units; Europe 25 / 91; Asia 2 (incl.
  TR counted Europe by NUTS) ; North America 2 / 59; South America 1 / 16.
- Median vintage gap: 17 years (dominant pairs 2002->2019; USDA fixed 2002->2022).

## Coverage gaps (honest)
- Not acquired: India, China, Russia, Australia, Argentina, Mexico, MENA (outside
  Yemen), Central Asia. These are documented NOT ACQUIRED in the audit CSV;
  the study is therefore **multi-region**, not fully global (see §17
  REPRESENTATIVENESS audit).
- Europe usable at admin-1 only in coarse crop classes (Eurostat regional table
  exposes ~10 aggregate classes, not detailed crops).
- Fraction of world harvested area covered by the design matrix baseline:
  ~0.34 Gha measured annual mean (≈25% of ~1.4 Gha world harvested area).
