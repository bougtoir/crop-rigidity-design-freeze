# 02 — Primary model family for continuous JSD (Issue 2)

## Observed outcome facts (primary sample, N=147)

- JSD ∈ [0, √ln 2 ≈ 0.8326]; observed range 0.0278–0.4093
- mean 0.1695, SD 0.0583; **no zeros**, no boundary mass
- normalized outcome y = JSD/√ln2 stays strictly inside (0, 1)

## Candidates evaluated (no β3 anywhere)

| Family | Assessment |
|--------|-----------|
| **A. Fractional logit / quasi-binomial** | ADOPTED. Naturally bounded mean, exact zeros/ones tolerated if they ever occur, quasi-likelihood robust to misspecified variance, log-odds coefficients interpretable, pairs with the frozen bootstrap inference. |
| B. Beta regression | Defensible (no observed 0/1 after scaling) but adds a precision parameter, is fragile if a boundary value ever appears, and offers no advantage over A for this estimand. Pre-registered robustness check only. |
| C. Transformed linear (logit/OLS) | Logit-transform destroys bounded-support guarantees for fitted mean near edges; plain OLS can predict outside (0,1). Robustness slot only. |
| D. Other bounded models | None clearly superior. |

Decision basis (as required): support of JSD, absence of zeros,
residual behavior under the no-interaction fit `JSD ~ HHI + mismatch`,
interpretability, robustness. **Not** chosen via any β3 significance.

## FROZEN

`logit(E[y_i]) = β0 + β1·HHI_i + β2·M_i + β3·HHI_i·M_i`, GLM binomial
family, quasi-binomial inference via the frozen bootstrap. y =
JSD/√ln2. β3 and its two-sided 95% CI are the primary estimand;
simulation (`scripts/09_power_simulation_v3.py`) generates bounded
continuous outcomes under this family preserving the observed design
matrix, JSD mean/dispersion, support, and dominant-mismatch × HHI
correlation (observed r = −0.036).
