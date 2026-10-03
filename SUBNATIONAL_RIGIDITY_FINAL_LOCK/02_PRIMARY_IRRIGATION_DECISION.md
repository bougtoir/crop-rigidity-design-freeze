# 02 PRIMARY IRRIGATION DECISION (frozen)

**Primary baseline irrigation exposure:**

```
irr_share_base2000 = Σ_crops SPAM2000 _I (irrigated harvested area)
                     / Σ_crops SPAM2000 _A (total harvested area)
```

zonal over each admin-1 geometry (same rasterization pipeline as the
previous SPAM2010 procedure; nodata cells excluded; share clipped [0,1]).

- Fallback fill: MIRCA2000 unit-level irrigated/(irrigated+rainfed) area
  where SPAM2000 zones had no cropland. Final sample required **0 fills**
  (all 369 units have SPAM2000 cropland pixels).
- Missingness rule (locked): units without a baseline irrigation value
  are excluded from the primary model; they cannot be exposed to the
  treatment being tested. 369/461 units satisfy all completeness rules.
- SPAM2010 zonal share remains as **predefined robustness** R-IRR-2010.
- USDA reported state irrigation (2002) remains I1 sensitivity check
  (documented construct difference).
- Distribution in final sample: mean 0.097, sd 0.178, long right tail
  (rainfed-dominant systems) — used untransformed; standardized only
  inside the information simulation.
- Within-country identifying variation: 38 countries; US, Nigeria,
  Indonesia, Tanzania, Brazil provide the bulk of within-country range.
