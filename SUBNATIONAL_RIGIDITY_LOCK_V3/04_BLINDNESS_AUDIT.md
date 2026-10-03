# 04 Blindness audit

Audit of every script/notebook/log in `crop_rigidity_design_freeze/` for
any fit of the real subnational outcome (`jsd`) on the interaction
design `irrigation × mismatch (+ controls, country FE)` prior to the
primary-analysis opening.

## Classification scheme

* **A** — no fit of the real outcome against the interaction design.
* **B** — outcome used *indirectly* in simulation (e.g. as a DGP baseline).
* **C** — real fit performed but never inspected/reported.
* **D** — real fit performed and inspected.

## Findings

| file(s) | class | detail |
|---|---|---|
| `scripts/43..51_*`, `spatial_inference_v3.py`, `information_simulation_v3.py` | A | no regression of observed `jsd` on `irr:mm` anywhere in the subnational pipeline; all sims generate synthetic outcomes |
| `scripts/48b_sims.py` (v2 info sim, superseded) | **B** | used observed unit-level `jsd` as the DGP baseline (`lam = clip(jsd + lin)`) — indirect outcome exposure, repaired in v3 |
| `scripts/49_scale_harmonization.py` | A | reads `jsd` only for sample completeness flags |
| `scripts/09_power_simulation_v3.py`, `10_spatial_inference_validation.py`, `20..24_*` (national phase) | **C** (national phase) | `sm.GLM(yobs, X[:, :3])` calibrated power against the *national* observed outcome; that phase is closed and its result archived — this exposure cannot contaminate the subnational estimand |
| logs / notebooks / docs | A | no stored output of any subnational b3 estimate exists |

## Judgment

* **Subnational analysis: effectively class A pre-analysis.** The only
  contamination path was the v2 simulation's use of observed JSD (class
  B). That simulation is superseded by `information_simulation_v3.py`
  (marginal-moment DGP; no unit-level outcome anywhere).
* Disclosed, not concealed: this document records the v2 exposure
  explicitly. Because the v2 sim informed only feasibility/power (not
  the estimand, sample, or estimator), the exposure does not compromise
  the confirmatory opening.
* The national primary fit (b3 = +0.0046) is a different unit of
  observation (country × crop) and stays archived; its existence does
  not unblind the subnational interaction.
