# 12 — Causal graph & covariate classification

DAG (text): irrigation <- geography/aridity/income -> mismatch & cropmix;
mismatch_T <- climate change x baseline geography; JSD <- baseline mix +
adaptation capacity <- institutions (country FE absorb).

- country fixed effects: confounder block (freeze).
- baseline HHI: confounder/control (correlates with mix structure) —
  classified control, mechanism only via hierarchy.
- baseline area, crop count: precision covariates.
- unit size/GDP proxies: unavailable -> documented.
- Collider guard: endline outcomes must not enter exposure or covariates.
  Irrigation is not randomly assigned: estimates are associational within
  country FE, and irrigation is plausibly a mediator of climate exposure —
  the interaction is the estimand, not the irrigation level effect.
