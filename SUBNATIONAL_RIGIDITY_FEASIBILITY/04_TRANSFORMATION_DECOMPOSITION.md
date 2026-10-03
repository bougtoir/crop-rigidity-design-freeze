# 04 — Transformation outcomes and the aggregation decomposition

## Candidate local outcomes (admin-1, observed stats)

| Outcome | Definition | Feasible |
|---|---|---|
| local crop-share JSD | JSD(share_t0, share_t1) within unit | yes (GSAP/Agro-MAPS, ≥2 vintages) |
| crop disappearance | crop share_t0 > θ, share_t1 = 0 | yes |
| crop entry | share_t0 = 0, share_t1 > θ | yes |
| crop replacement | dominant crop changes | yes |
| harvested-area reallocation | |Δ share| mass | yes |
| crop-centroid movement | movement of production centroid across units | yes (aggregate stat) |
| abandonment of cells | requires pixel truth | **modelled only — sensitivity layer** |
| irrigated↔rainfed transition | share of _I area | partial (SPAM I-split; admin irrigation stats where reported) |

## The decomposition (H4's formal core)

For each country c and period:

```
National transformation  T_c = JSD(national share_t0, share_t1)
Within-location switching W_c = Σ_u w_u · JSD(share_{u,t0}, share_{u,t1})
Between-location reallocation B_c = T_c − W_c  (JSD is decomposable
  non-linearly; B_c defined residually — same construction the national
  study used for JSD, applied hierarchically)
```

`w_u` = unit's share of national harvested area at baseline.
B_c measures how much of national change is achieved by *where* crops are
grown rather than *what* each unit grows. H4's test: B_c/(T_c) larger in
countries whose units have high average fixed-capital exposure; and
within units, mismatch × fixed capital → lower local JSD (rigidity)
coexisting with high national T_c.

## Can the national null coexist with local rigidity?

Yes, mechanically: national JSD (mean 0.17 in the completed study) can be
generated entirely by between-unit reallocation (B_c ≫ 0) with
W_c ≈ 0. The pilot shows the same signature in pixels: wheat national
|Δ| 5.4 Mha vs gross pixel churn ≈ 23% L1 — apparent local change
dwarfs net national change in *both* directions depending on
aggregation. The question the new study asks is which side dominates in
the *observed* data — this is an estimable, non-tautological quantity.
