# 13 — Identification design (frozen)

Within-country identification with country fixed effects; unit-level exposures.
Effective information (analysis/within_country_information.csv + design matrix):
- 51 countries, 461 units before exposure filters; 335 units/24 countries pass
  country>=3-units + complete exposure data.
- Within-country SD: irrigation >0.02 in 16 countries; mismatch_T >0.1 degC in
  24; perennial_strict >0.01 in 11. Within-country identification for
  H_PERENNIAL is therefore thin -> flagged as power-limited hypothesis.
- No single country dominates (largest = US 50 units, Nigeria 37, EL 30).
