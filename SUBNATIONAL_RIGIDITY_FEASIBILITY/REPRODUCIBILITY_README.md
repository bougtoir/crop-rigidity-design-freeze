# Reproducing SUBNATIONAL_RIGIDITY_FEASIBILITY

This package is a feasibility/design audit, not a hypothesis analysis.

- `scripts/30_spam_vintage_pilot.py` — extracts WHEA/MAIZ/RICE
  all-technology harvested-area rasters from the persisted SPAM2005 and
  SPAM2010 zips (`data/raw/mapspam/`), computes pixel-level
  correlation/disappearance/entry/L1 statistics and the same statistics
  after block-aggregation to 0.5°, 1.5°, 2.5°; writes
  `analysis/spam_vintage_pilot.json`. Deterministic (no RNG).
- Requires: rasterio, numpy, the two zip files (already persisted with
  SHA-256 in the parent project's DATA_SOURCE_LEDGER_v4.csv).

All other deliverables are audit documents derived from the cited
literature and the pilot numbers; they contain no fitted models.
