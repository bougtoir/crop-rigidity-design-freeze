# 03 Primary interpretable effects (original JSD scale)

Locked contrast: `Delta_ME = β3 × (I_P75 − I_P25) × SD(mismatch_T)`
(I_P75 = 0.0320, I_P25 = 0.0037, SD(M) = 0.5221 °C),
with marginal effects of +1 SD mismatch at irrigation P25/P50/P75.

| effect | point | 95% CI (bootstrap) |
|---|---|---|
| **Delta_ME** | **−0.0015** | [−0.0101, +0.0031] |
| ME_P25 | −0.0028 | [−0.0271, +0.0284] |
| ME_P50 | −0.0031 | [−0.0266, +0.0268] |
| ME_P75 | −0.0043 | [−0.0262, +0.0223] |

Delta_ME ≈ −0.002 JSD units: essentially zero — no detectable
conditioning of the mismatch–transformation relationship by baseline
irrigation dependence at this scale and precision. No causal language
is used; no direction is labelled good or bad.

Figures 1–4 in `figures/` stay within observed irrigation/mismatch
support.
