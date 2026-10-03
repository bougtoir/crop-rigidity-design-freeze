# 03 — Environmental mismatch protocol

Exposure must represent **mismatch**, not warming per se.

## Primary definition (frozen before outcome association)

For each country i:

1. identify the legacy dominant crop c*(i) = crop with the largest mean
   harvested-area share in 1981–2000;
2. construct the **baseline climate niche** of c*(i) from GAEZ/ISIMIP-era
   climatology: the joint distribution of growing-season mean temperature and
   precipitation over all grid cells where c*(i) was actually grown
   (MapSPAM 2005 harvested-area mask) during the reference period;
3. compute **Mismatch_i** = Mahalanobis distance between (a) the 2001–2020
   growing-season climate experienced over the same footprint and (b) the
   baseline niche distribution, using the baseline covariance.

This is the primary metric because it is (a) agronomically interpretable —
distance from the climate in which the inherited crop was embedded; (b)
multivariate in T and P; (c) defined entirely by the legacy crop and baseline
climate, independent of the transformation outcome.

## Predefined secondary mismatch measures (multiverse members, not primary)

- standardized growing-season temperature anomaly (2001–2020 vs 1961–1990);
- standardized precipitation anomaly (same contrast);
- GAEZ suitability-index change for the legacy dominant crop
  (RES05-SCI class change TP-2010 → TP-2070 used only in the counterfactual
  module; an ERA5-Land/W5E5-derived contemporary counterpart joins the
  observational model);
- extreme-heat exceedance: change in frequency of days above the crop's upper
  optimal threshold (NASA POWER daily T2M_MAX, crop thresholds from MIRCA/GGCMI
  crop calendars);
- SPEI-12 drought-frequency change (SPEIbase v2.11, acquired).

## Selection rule (binding)

The primary metric was chosen on agronomic grounds *before* any outcome
regression is run. Under no circumstances is the mismatch metric re-selected
because an alternative yields a more desirable interaction sign. If the
Mahalanobis construction proves uncomputable for a country (insufficient crop
footprint), that country is excluded with an explicit code in the missingness
log — the metric is not swapped per-country.

## Data status at freeze

- MapSPAM masks for dominant-crop footprints: acquired (2005, 2010).
- Contemporary climate: NASA POWER API verified reachable (200 + sample JSON);
  SPEIbase v2.11 netCDFs (spei01, spei12) downloaded; ISIMIP3b LPJmL outputs
  downloaded for GFDL-ESM4 and IPSL-CM6A-LR (2 GCMs) for the counterfactual arm.
- ERA5-Land/ERA5 via CDS requires credentials not available in-session;
  W5E5 (the ISIMIP forcing, ERA5-family) substitutes and is documented as such.
