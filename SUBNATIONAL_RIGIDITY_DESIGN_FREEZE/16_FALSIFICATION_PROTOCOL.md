# 16 — Falsification protocol (14 predefined tests, frozen)

F1 pre-treatment mismatch (2000-2005 vs 1995-1999 where available) must be ~0.
F2 shuffled exposures within country -> ~5% rejection.
F3 placebo outcome: JSD computed on shuffled crop labels -> ~null.
F4 placebo window: endline pair [2013,2016] short gap -> attenuated effect.
F5 sign flip of mismatch (negated) -> sign consistency check.
F6 drop largest country (US) -> effect robustness.
F7 drop Eurostat block -> non-EU robustness.
F8 A-grade-only temporal comparability subset.
F9 area-weighted regression vs unweighted.
F10 dominant-crop-only mismatch variant.
F11 extended crop set outcome variant.
F12 broad perennial exposure variant.
F13 USDA-reported irrigation (I1) for US subsample.
F14 exclude units with GADM-unmatched boundaries.
