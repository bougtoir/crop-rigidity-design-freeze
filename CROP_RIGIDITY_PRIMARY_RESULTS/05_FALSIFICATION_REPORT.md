# 05 — Falsification report

Pre-registered falsification suite plus the mandatory audit rows. Primary
β3 = +0.0046 [−0.131, +0.143] for reference.

| # | Test | β3 | 95% CI / range | Verdict |
|---|---|---|---|---|
| F1 | Future exposure (2011–2020 climate) vs near-term outcome (2002–2010 JSD) | −0.017 | [−0.197, +0.108] | Pass (null) |
| F2 | Wrong temporal exposure window (1984–1990 → 1991–2000 mismatch vs frozen outcome) | +0.142 | [+0.062, +0.289] | **Flag: positive** — see below |
| F3 | Geographically displaced exposure (region-off permutation, 200×) | +0.005 median | [−0.090, +0.098] | Pass (null distribution centered on 0) |
| F4 | Leave-one-region-out | — | β3 ∈ [−0.011, +0.088] | Pass (stable) |
| F5 | Leave-one-subregion-out | — | β3 ∈ [−0.010, +0.034] | Pass (stable) |
| F6 | Exclude OTHE-dominant countries | +0.005 | [−0.130, +0.131] | Pass (identical; n=147 means none were OTHE-dominant) |
| F7 | Exclude <15y legacy reporting | +0.004 | [−0.158, +0.160] | Pass |
| F8 | Missingness covariates (excluded n=36 vs included n=147) | — | hhi 0.34 vs 0.23; jsd 0.21 vs 0.17 | Audit: excluded countries are more specialized and transformed more — exclusion is not random; bounds on generalizability, not on the internal estimate |
| F9 | Pre-trend: 1981–90 → 1991–01 JSD vs frozen mismatch | −0.099 | [−0.203, +0.041] | Pass (CI covers 0; point estimate mildly negative, opposite to F2) |
| F10 | Null permutation of mismatch (500×) | real +0.005 | permuted range [−0.106, +0.095] | Pass (real estimate inside null) |

## F2 — the one discordant result (reported, not suppressed)

Replacing the exposure window with a pre-treatment climate contrast
(1984–1990 vs 1991–2000 mismatch, evaluated against the frozen outcome)
yields β3 = +0.142 [+0.062, +0.289]. This is a *positive* flag: it means
specialization-conditioned mismatch exposure was already correlated with
later transformation before the frozen treatment period. Interpretations:

- consistent with baseline drift/confounding in the HHI–mismatch–JSD system
  (e.g. specialized countries already on divergent trajectories); or
- an artefact of the 1980s-90s climate contrast picking up different
  geography (pre-treatment mismatch uses the same MIRCA calendar baseline
  construction but a different climate delta).

It does **not** rescue or overturn the primary null: the frozen estimand is
the 2002–2020 exposure contrast, and F2 is a falsification of a different
regression. But it honestly weakens any causal reading of small positive
point estimates across the ledger (B, D, E all +): the pre-treatment
analogue shows similar-signed correlation. Reported verbatim in
`analysis/falsification_results.csv`; labeled PRE-REGISTERED, not post hoc.
