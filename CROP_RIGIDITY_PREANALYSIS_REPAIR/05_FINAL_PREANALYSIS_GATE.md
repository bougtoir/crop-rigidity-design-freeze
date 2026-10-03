# 05 — Final Pre-Analysis Gate

| # | Criterion | Verdict | Evidence |
|---|-----------|---------|----------|
| 1 | Primary mismatch uses baseline-period crop geography | PASS | SPAM2000 (avg 1999–2001) footprints; `00_`, `analysis/footprint_cells.csv` |
| 2 | No post-treatment crop footprint enters the primary exposure | PASS | MapSPAM 2005 removed from the exposure chain; exposure = post-2001 climate evaluated on the pre-2001 footprint/niche only |
| 3 | Primary mismatch successfully calculated on real data | PASS | `analysis/primary_mismatch_country.csv`: 130/164 estimation countries with finite Mahalanobis distance; missingness enumerated |
| 4 | Covariance diagnostics acceptable | PASS | `analysis/mismatch_diagnostics.csv`: condition number median ~34 (max ~434); Ledoit–Wolf single common rule; full-shrink cases flagged; missing T/P fraction 0 |
| 5 | Dominant vs portfolio resolved without outcome | PASS | `02_`: decision made on correlation/coverage/missingness only (corr 0.998); no outcome model run |
| 6 | Taxonomy avoids aggregate/double-counting | PASS | `FAOSTAT_CROP_ITEM_AUDIT.csv`: 14 aggregate items excluded explicitly by name/code; green/dry sibling pairs flagged; HHI/JSD recomputed in `corrected_cropmix_diagnostics.csv` (median ΔHHI +0.057, ΔJSD +0.024 vs the regex-based freeze diagnostics — the correction matters and is reported) |
| 7 | Geographic clustering authoritative + reproducible | PASS | `COUNTRY_REGION_CROSSWALK.csv` via country_converter (UN M49-aligned); historical/aggregate entities excluded and named, never silently reassigned |
| 8 | Effective-information analysis matches the inferential method | PASS | `03_` + `analysis/power_simulation_v2.csv`: sims run on observed L/M/sample/regions; 5-cluster CRVE shown anti-conservative (15% null rejection) → primary inference frozen to subregion spatial-block bootstrap |
| 9 | Data/handoff manifest internally consistent | PASS | `PACKAGE_MANIFEST.csv` + `scripts/05_validate_manifest.py` (exit 0); approach B confirmed — no raw data shipped |
| 10 | No primary metric selected using β3 | PASS | β3 has never been estimated; all choices frozen on design/data grounds |

## DECISION: GO TO FULL ANALYSIS

With documented deviations: baseline climate window 1984–2000 (POWER
coverage; still strictly pre-treatment), 130-country mismatch coverage,
and honest power (~60% at moderate interactions; strong effects
detectable). Claim discipline per Issue 9 applies.

## Issue 9 — novelty discipline (binding)

- Classification **B** maintained. No named "law".
- Forbidden claims: civilization causes decline; specialization is
  harmful; sign reversal of civilizational capital; Retention Burden is
  universally positive; "first global study" unless the literature audit
  supports that exact statement.
- Strongest defensible claim:
  *"Pre-existing production structure may condition the extent to which
  crop systems reorganize under climatic mismatch."*
