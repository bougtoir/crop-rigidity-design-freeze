# 07 Falsification report

`analysis/falsification_results.csv`. Pre-registered vs post-hoc
flagged; no post-hoc test replaces the primary.

| test | β3-type estimate | CI | status |
|---|---|---|---|
| F1 wrong climate var (precip) | −0.019 [−0.134,+0.181] | — | pre-reg |
| F2 spatially shifted mismatch | −0.077 [−0.316,+0.065] | — | pre-reg |
| F3 MIRCA2000 irrigation (N=258) | +0.032 [−0.270,+0.419] | — | pre-reg |
| F4 sparse-reporting exclusion (N=228) | −0.030 [−0.387,+0.066] | — | post-hoc |
| F5 L1 outcome metric | −0.094 [−0.517,+0.201] | — | post-hoc |
| F6 null spatial permutation (999×) | null dist mean ≈ 0 [−0.161,+0.155]; observed |b3| inside it (p=0.63) | — | pre-reg |
| F7 NUTS2 scope | see ledger (−0.028) | — | pre-reg |

All falsifications return estimates consistent with the null-weak
primary; the permuted null envelops the observed interaction.
LOCO/LORO were run as robustness (Part E.9–10) and are stable.
