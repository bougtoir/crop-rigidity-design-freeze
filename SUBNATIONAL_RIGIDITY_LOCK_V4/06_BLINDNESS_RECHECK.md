# 06 Blindness recheck (v4)

Re-grep of every file for any regression of observed subnational JSD on
irrigation × mismatch (or equivalent):

* `scripts/60..` v3/v4 pipeline, `spatial_inference_v4.py`,
  `information_simulation_v4.py`: all fits use synthetic outcomes;
  observed `jsd` is read only for (a) sample completeness, (b) the
  five-number marginal summary in `jsd_marginal_summary_v4.csv` —
  explicitly permitted (marginal moments, not a conditional fit).
* No CSV, log, notebook or doc anywhere contains a real subnational
  β3 or a fit equivalent to it.
* v2 sim exposure (class B) still superseded; v3 linear sim superseded
  by v4 bounded DGP.

Classification: **A** for the subnational headline estimand —
no real fit exists. (Peripheral class-B/C rows from 04_BLINDNESS_AUDIT
remain disclosed, unchanged.)
