# 03 — Temporal boundary repair (Issue 3)

## Problem

SPAM2000 v3.0.7 is `avg(1999–2001)`, so it contains calendar-year-2001
information. A "strictly pre-treatment" claim for a 2001-start
exposure/outcome window was therefore too strong.

## Resolution — adopted as PRIMARY

Strict post-baseline boundary moved to **2002**. Frozen temporal ladder:

| Layer | Window |
|-------|--------|
| Legacy crop mix | 1981–2001 |
| Baseline footprint | SPAM2000 avg(1999–2001) |
| Baseline climate niche | 1984–2001 (POWER monthly coverage floor) |
| Environmental mismatch | 2002–2020 |
| Transformation outcome | crop mix 1981–2001 → crop mix 2002–2020 |

Ordering is now clean: legacy/footprint/baseline ≤ 2001 < exposure/
transformation ≥ 2002. The old 1981–2000/2001–2020 ladder is retained
as a predefined sensitivity analysis only.

## Materiality check (`analysis/temporal_boundary_diagnostics.csv`)

Endpoint shift 2000→2001 across all 209 countries with valid mix data:

- ΔHHI: median −0.00033
- ΔJSD: median −0.00072, max |Δ| = 0.057
- dominant crop changed: 2 / 209 countries
- sample size: unchanged (229 valid-mix entities → same attrition class)

Changes are negligible → the strict 2002 boundary is PRIMARY.
"No post-treatment information enters the baseline" is now defensible:
all baseline layers end in 2001, all exposure/outcome layers begin in
2002. β3 was not touched anywhere in this check.
