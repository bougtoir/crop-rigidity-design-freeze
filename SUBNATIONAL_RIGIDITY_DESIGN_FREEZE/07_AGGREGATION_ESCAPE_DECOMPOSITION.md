# 07 — Aggregation-escape decomposition (repaired)

The feasibility design wrote T = W + B on Jensen-Shannon distance. That is NOT a
valid additive decomposition: JSD is nonlinear in the group-aggregated
composition, and within/between components so defined mechanically encode the
exposure.

Repair adopted (computed on observed matrices):
- Do NOT decompose JSD. Decompose the **national crop-share change** per crop k:
    Delta_k = W_k + B_k + I_k
  W_k = sum_u w0_u (p1_uk - p0_uk)   (within-unit crop shift)
  B_k = sum_u p0_uk (w1_u - w0_u)    (reallocation of area between units)
  I_k = residual interaction (Das Gupta two-factor, exact)
  This is an exact additive decomposition of the observed aggregate change;
  components are interpretable, do not encode the exposure, and satisfy
  Delta_k = W_k + B_k + I_k to machine precision (validated on all 52
  country-vintage pairs; max residual 0.0 — see
  analysis/decomposition_method_validation.csv).
- Empirical finding (for the protocol report): within-unit change carries
  ~80% of absolute share change on average across countries (median 0.83),
  i.e. the aggregation escape exists but is not dominant in-sample.
- JSD remains the primary within-unit outcome; the decomposition is the
  system-level (H_AGGREGATION) measure. JSD_T/W/B language removed.
