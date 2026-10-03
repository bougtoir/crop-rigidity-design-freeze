# 03 — Primary effect sizes (frozen contrasts)

Marginal effect of +1 SD climatic mismatch on JSD, evaluated at the locked
HHI percentiles. Delta_ME = ME_P75 − ME_P25. Negative Δ = specialization
attenuates the mismatch–transformation association; ≈ 0 = no detectable
conditioning; > 0 = amplifies. No normative label is attached.

| Contrast | Estimate (JSD) | 95% CI |
|---|---|---|
| ME at HHI P25 (0.110) | −0.0020 | [−0.015, +0.010] |
| ME at HHI P50 (0.186) | −0.0017 | [−0.012, +0.007] |
| ME at HHI P75 (0.334) | −0.0012 | [−0.014, +0.014] |
| **Δ_ME (P75 − P25)** | **+0.0007** | [−0.018, +0.021] |

Reading: the marginal effect of a 1-SD climatic mismatch on crop-mix
transformation is ≈ 0 at every point of the specialization distribution
(observed JSD mean 0.170, SD 0.058). The difference between the most and
least specialized quartiles is +0.0007 JSD — ~1% of the outcome SD — with a
CI that excludes anything beyond ±0.02 JSD. Under the frozen interpretation
rule this is "no detectable conditioning".

Source: `analysis/primary_effects.csv`, `analysis/primary_bootstrap_replicates.csv`.
