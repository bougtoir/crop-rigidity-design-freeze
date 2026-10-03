# DECISION: GO TO SUBNATIONAL PRIMARY ANALYSIS (multi-region scope)

All ten gate conditions evaluated against realized data (not intentions):

1. Comparable observed admin crop vintages: PASS — 461 admin-1 units, 51
   countries, 2+ vintages, gap median 17y.
2. Harmonized boundaries defensible: PASS w/ caveat — all retained units carry
   source-stable identifiers; 107 NUTS code-churn units dropped (unresolved);
   GADM4.1 match 47% is a reporting frame only, not a joint.
3. Coverage broad for claimed scope: PASS AS MULTI-REGION — Africa/Europe/
   Americas/Asia covered; India/China/Russia/Australia NOT acquired → the
   study is labelled multi-region, not global.
4. Irrigation interpretable & pre-outcome: PASS — SPAM 2010 zonal share
   (endline-adjacent but fixed-period, not outcome-derived); USDA reported
   as sensitivity; num/den alignment enforced.
5. Crop-calendar mismatch temporally clean: PASS — POWER centroids +
   MIRCA national calendars; no outcome leakage.
6. Primary outcome meaningful: PASS — within-unit JSD on observed shares;
   realized median 0.22.
7. Within-country identifying variation: PASS w/ flag — irrigation/mismatch
   adequate (16/24 countries); perennial_strict thin (11 countries) →
   H_PERENNIAL is underpowered and stays secondary.
8. Spatial inference validated: PASS — within-country block bootstrap
   type-I 6.7%; country CRVE anti-conservative (15.7%) demoted.
9. H4 decomposition defensible: PASS — JSD decomposition abandoned; exact
   Kitagawa decomposition of share change validated to machine precision.
10. No headline inspected: PASS — no exposure×outcome interaction was
    estimated; outcome distributions were used only for power simulation
    on simulated effects.

Residual risks: coarse Eurostat crop classes; MIRCA national calendars proxy
admin-1 calendars; multi-region label binding.
