# 07 TEMPORAL ALIGNMENT NOTE

`analysis/admin_temporal_alignment_audit.csv` — one row per unit:

- `y0`, `y1`: that unit's actual agricultural baseline/endline years
  (nearest-observation rule per source, gap ≥ 8 y; median 17 y)
- `climate_base_window` = [y0−1, y0+1], `climate_end_window` = [y1−1, y1+1]
  — each unit's climate is computed over **its own** agricultural
  endpoints with an explicit ±1-year smoothing rule
- `aligned` = True for all 461 units

Mismatch_T is therefore a per-unit (y0→y1) climate change, not a global
2002→2019 comparison applied to differing agricultural pairs. The ±1
smoothing is the disclosed tolerance; it dampens endpoint weather noise
without changing the exposure construct.

No unit carries an agricultural pair whose climate windows were computed
on a different interval.
