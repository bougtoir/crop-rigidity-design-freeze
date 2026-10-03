# 03 — Method-change report / temporal comparability

Grade rule: A = same instrument, stable units, both vintages; B = documented
format/method revision that does not alter variable definitions; C = definitional
change requiring harmonization; D = unusable.

- No source graded D survives in the design matrix.
- IBGE PAM: pre-2017 tables ship per-crop UF xls, post-2016 consolidated state
  xls; harvested-area columns equivalent -> B.
- Eurostat: OBS_FLAG 'b'/'d' rows flagged; NUTS revision churn handled by the
  boundary protocol (unresolved units dropped) -> B for retained units.
- HarvestStat: qc_flag rows retained (reported observations); modelled gap-fills
  excluded -> A.
- Primary analysis uses grade A/B only (frozen).
