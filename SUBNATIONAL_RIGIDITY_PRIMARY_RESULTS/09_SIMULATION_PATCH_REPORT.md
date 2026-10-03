# 09 Simulation patch report — information_simulation_v4_1

## The bug

v4's `contrast_for_b3()` evaluated the +1/-1 SD mismatch counterfactual
as `±b3·z_int` using the interaction computed at each unit's *original*
mismatch — equivalent to sign-flipping rather than shifting. The
correct contrast requires recomputing `z_int` at the shifted mismatch
with the same frozen standardization.

## The fix

`z_int(mm') = (z_irr·mm' − m0)/s0`, `m0,s0` from the observed product.
Up: `mm' = z_mm + 1`; down: `mm' = z_mm − 1`.

## Effect on the mapping (200 reps/scenario, B=80 boot)

| target JSD | latent b3 (v4.1) | achieved | induced OLS int | coverage | power |
|---|---|---|---|---|---|
| 0.00 | 0.000 | −0.0172* | −0.0041 | 0.955 | type-I 0.050 |
| +0.01 | +0.049 | +0.0100 | +0.0061 | 0.975 | 0.045 |
| +0.02 | +0.067 | +0.0200 | +0.0094 | 0.960 | 0.070 |
| +0.04 | +0.102 | +0.0400 | +0.0152 | 0.980 | 0.230 |
| −0.01 | +0.013 | −0.0100 | −0.0012 | 0.965 | 0.030 |
| −0.02 | −0.005 | −0.0200 | −0.0052 | 0.985 | 0.050 |
| −0.04 | −0.042 | −0.0400 | −0.0137 | 0.980 | 0.080 |

*At b3=0 the population JSD-scale contrast is −0.0172, not 0: logistic
curvature plus the sample's irrigation–mismatch covariance induce a
small baseline contrast even with no interaction. This is the correct
feature of a bounded DGP and is why small negative targets need only
small latent adjustments. The mapping is now directionally coherent
and monotone.

## Consequence for inference

Under the corrected mapping, |Δ_ME| ≤ 0.04 JSD-unit effects correspond
to small latent interactions and are partially inside the noise floor
(grid10 CI half-width ≈ 0.055 on the standardized interaction scale):
power at these effect sizes is 3–23%. This bounds — honestly — the
smallest conditioned effect the frozen design could detect. It does
not change the estimator, sample, or lock.
