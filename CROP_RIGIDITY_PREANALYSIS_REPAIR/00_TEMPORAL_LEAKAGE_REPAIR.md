# 00 — Temporal Leakage Repair

## Problem

The design-freeze package used MapSPAM 2005 to define baseline crop
footprints. SPAM 2005 is an allocation of **2005-era** production: it
post-dates the 2001 treatment boundary and is itself a realization of
post-treatment adaptation. Using it to define "where the legacy crop
grew" is post-treatment leakage.

## Resolution

The baseline footprint is now built from **SPAM 2000 v3.0.7**
(IFPRI, Dataverse `doi:10.7910/DVN/A50I2T`), which allocates production
centred on 1999–2001 (`year_data = "avg(99-01)"`) — entirely consistent
with a pre-treatment baseline. Both the GeoTIFF stack and the DBF-CSV
per-pixel table (`spam_h.csv`: `stat_code` = ISO3, `x`,`y` = pixel
centre, per-crop harvested area) were acquired; the pixel table is used
directly for footprint cell extraction.

Hierarchy compliance: option (1) — a product dated at or before 2000 —
is used; no fallback was required.

## Frozen temporal ladder (final)

| Quantity | Window | Source |
|---|---|---|
| Legacy crop mix | 1981–2000 | FAOSTAT QCL (OWID mirror 2026-02-25) |
| Baseline crop footprint | ~1999–2001 | SPAM 2000 v3.0.7 |
| Baseline climate niche | **1984–2000** (see deviation) | NASA POWER monthly |
| Mismatch exposure window | 2001–2020 | NASA POWER monthly |
| Outcome mix change | 1981–2000 → 2001–2020 | FAOSTAT QCL |

### Deviation: baseline climate window 1984–2000 (not 1961–1990)

NASA POWER monthly series begin **1984-01**. No product in the acquired
set provides monthly T and P for 1961–1983 at the needed resolution
inside the VM's network reach (CRU TS and ERA5/CDS are not reachable;
W5E5 per-year files are multi-GB global rasters). The baseline climate
window is therefore set to **1984–2000**: 17 complete pre-treatment
years. The substantive requirement — the niche baseline contains no
post-2001 information — is preserved. This deviation is recorded here
and in the ledger; it does not alter the exposure/outcome windows.

## Crosswalk

`SPAM_FAOSTAT_CROSSWALK.csv` maps every FAOSTAT item to its SPAM2000
class. Coverage: every kept FAOSTAT item maps to one of the 21 SPAM
classes (20 crops + OTHE residual). Cross-crop FAOSTAT aggregates
(Cereals, Pulses, Roots and tubers, etc.) are marked `no SPAM class`
and are excluded upstream by the item audit — no crop is silently
dropped; unmatched items are named in the crosswalk.

## What changed vs design freeze

- Footprint source: MapSPAM 2005 → **SPAM 2000 v3.0.7** (pre-treatment).
- Climate baseline: 1961–1990 → **1984–2000** (data-availability
  deviation, documented).
- `analysis/footprint_cells.csv` now maps each country × SPAM crop to
  its occupied grid cells, binned to the NASA POWER grid.
