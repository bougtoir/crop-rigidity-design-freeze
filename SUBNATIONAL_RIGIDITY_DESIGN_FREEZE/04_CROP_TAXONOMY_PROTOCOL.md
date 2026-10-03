# 04 — Crop taxonomy protocol (frozen)

Canonical set maps every source crop string to a FAOSTAT-style item + MIRCA
class + lifecycle (04_CROP_CROSSWALK.csv, one row per source crop, 100%
of observed strings classified; unmapped share of total area = 0.003%).

- PRIMARY_CROP_SET (28 canonical groups incl. `other_remainder` tail):
  wheat rice maize barley sorghum millet cassava potato sweet_potato yams
  sugarcane soybean groundnut rapeseed sunflower cotton dry_beans cowpea
  coffee cocoa tea oil_palm banana other_cereals other_roots other_pulses
  other_oilseeds other_perennial.
- EXTENDED_CROP_SET = PRIMARY + chickpea pigeon_pea lentil field_pea oats rye
  triticale sugar_beet sesame plantain pineapple citrus grapes apple mango
  dates cashew olive tobacco tomato onion vegetables spices khat sisal forage.
- Aggregate rows (`lavouras temporarias`, `wheat, all`, cereal totals, etc.) and
  noncrop rows (fallow, seeds, flowers, UAA, kitchen gardens) are dropped to
  prevent double counting.
