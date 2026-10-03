# 08 CALENDAR PROXY VALIDATION

`analysis/calendar_proxy_validation.csv`.

The primary mismatch uses MIRCA2000 **national** crop calendars applied
to admin-1 units. MIRCA stores admin-1 calendars for 7 large countries
(USA, Brazil, Indonesia, Argentina, Australia, China, India); 3 of them
are in our sample (USA 50, Indonesia 29, Brazil 16 units).

For every sample unit in those countries we recomputed mismatch_T twice:

- `mismatch_national`: country's MIRCA national calendar (for
  MIRCA-subnational countries: area-weighted aggregate of their
  subnational calendars)
- `mismatch_subnat`: the unit's own admin-1 MIRCA calendar

## Result

- 26 units matched (US states, Brazilian states; Indonesian units are
  only "Java"/"Outside Java" so few matched by name)
- corr(national, subnational) = **0.992**
- median |Δ| = 0.027°C

## Decision

National-calendar approximation **retained** with explicit limitation:
it assumes planting months are national invariants — acceptable for
temperature-mismatch ranking (corr 0.99) and documented as an
approximation, not as ground truth. A predefined robustness R-CAL-SUBNAT
recomputes mismatch_T with admin-1 MIRCA calendars where they exist.
