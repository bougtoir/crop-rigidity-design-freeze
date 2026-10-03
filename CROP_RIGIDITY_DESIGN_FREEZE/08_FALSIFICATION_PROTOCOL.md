# 08 — Falsification protocol (frozen)

All tests below are predefined; none may be dropped because its result is
inconvenient. A "pass" means the diagnostic pattern expected under a spurious
association is absent.

| # | Test | Construction | Expected under a real effect |
|---|---|---|---|
| 1 | Placebo future exposure | regress legacy-to-legacy-period transformation on *future* (2021–2040 projected W5E5/ISIMIP) mismatch | β3 ≈ 0 — the future cannot cause the past |
| 2 | Temporally displaced exposure | mismatch computed 1971–1990 against primary windows | attenuation toward 0 |
| 3 | Spatial displacement | climate field shifted ~10° latitude within hemisphere | β3 ≈ 0 |
| 4 | Leave-one-region-out | drop each UN macro region in turn | sign/magnitude stable; no single region drives β3 |
| 5 | Alternate crop sets | restrict to major staples (≥1% global area) / exclude minor crops | consistent β3 |
| 6 | Sparse-reporting exclusion | drop bottom-decile FAO coverage countries | consistent β3 (spec M01) |
| 7 | Missingness weighting | inverse-probability weights for inclusion in both windows | consistent β3 |
| 8 | Pre-trend analysis | JSD(1961–1980 vs 1981–2000) as a function of legacy HHI interacted with *past* mismatch | validates ordering; not a causal claim |
| 9 | Negative-control exposure | an environmental series unrelated to crops (e.g. SPEI over non-cropland mask or ocean-adjacent grid cells) | β3 ≈ 0 |
| 10 | Simulated null | outcome replaced by Gaussian noise preserving the empirical covariance of (Mismatch, Legacy, X) | β3 distribution centred at 0; provides an empirical reference band |

## Rules

- Tests 1–3 are sharp placebos; failure (non-null β3) invalidates the primary
  interpretation and triggers redesign, not post-hoc patching.
- Tests 4–7 are robustness; instability is reported, not hidden.
- Test 10 generates the empirical null band used in 10_INFORMATION_ASSESSMENT.
- Results for the full battery are reported in a single falsification table in
  the eventual analysis report.
