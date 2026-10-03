# 09 H4 DECOMPOSITION — FINAL TERMINOLOGY

Kitagawa (Oaxaca-type) exact decomposition retained; JSD residual
decomposition is NOT revived.

For each crop k and country:

```
Δ_k = W_k + B_k + I_k

W_k = within-unit crop-share change (area weights fixed at baseline)
B_k = redistribution of total agricultural area between units
I_k = interaction between the two
```

## Reporting rule (frozen)

- B_k alone is never described as "adaptation escape": W, B and I move
  jointly, so any single-term label misleads.
- National summaries report **absolute contributions** |W|,|B|,|I|
  (share of total absolute change) **and** the signed decomposition
  separately.
- Validation (design-freeze package, `decomposition_method_validation.csv`):
  exact identity to machine precision on 52 country-vintage pairs;
  within-unit ≈ 80% of absolute change.
- H4 remains **system-level secondary/descriptive**: no inferential test
  on the decomposition is frozen in this lock. If H4 is to carry
  inference, a separate protocol must be frozen first.
