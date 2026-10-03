# FINAL_HANDOFF — crop rigidity, locked primary analysis

## The contract

`PRIMARY_ANALYSIS_LOCK.yaml` (SHA-256 in `.sha256`) is the single
binding definition. The next session:

- reads `analysis/primary_sample_preoutcome.csv` (N=147) as the
  estimation set;
- fits `logit(E[jsd/√ln2]) = β0 + β1·HHI + β2·M + β3·HHI·M` —
  fractional logit, standardized HHI and dominant-crop crop-calendar
  mismatch;
- reports β3 two-sided 95% CI via M49-subregion cluster bootstrap
  (B=999, seed 20261003);
- reports the frozen contrasts: ME(+1 SD mismatch) at HHI P25/P50/P75
  and Δ_ME = P75−P25, on the JSD scale;
- reports precision (CI width) alongside significance.

## Pre-registered non-primary rows

- Geographic block bootstrap (30° tiles) as secondary inference;
  HC2 as conservative bound only. Conley SE and region-level CRVE are
  PROHIBITED as primary.
- Old temporal ladder (1981–2000/2001–2020) sensitivity.
- Lagged sensitivity: legacy 1981–2000 → exposure 2001–2010 →
  transformation 2011–2020.
- Thermal-season climatic displacement exposure (renamed >5°C rule).
- Portfolio calendar mismatch under ≥0.70 coverage (0.50/0.80
  sensitivities).
- Beta regression on (0,1)-scaled JSD; transformed linear — robustness
  family slots.

## Prohibited

- Modifying `PRIMARY_ANALYSIS_LOCK.yaml` (checksum audit on handoff).
- Any exposure/outcome substitution based on estimated associations.
- One-sided testing; dichotomizing JSD for the primary estimand.
- Portfolio values below the coverage floor.

## Claim ceiling (unchanged, binding)

Class B novelty; no named law; no "civilization causes decline", no
"specialization is harmful", no sign-reversal claims, no "first global
study". Strongest claim: *"Pre-existing production structure may
condition the extent to which crop systems reorganize under climatic
mismatch."*
