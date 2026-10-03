# 06 — Outcome protocol (frozen)

Primary outcome: **JSD** between baseline and endline canonical-crop share
vectors within unit u (share of harvested area over PRIMARY_CROP_SET +
other_remainder). Continuous; JSD is bounded, symmetric, finite-sample stable.

Frozen details:
- Zero handling: implicit 0 shares; JSD evaluates p log p/q only where p>0.
- Min coverage: unit must report >=3 canonical crops with positive area at each
  vintage; total baseline area > 0.
- Normalization: shares over the retained set (not world-coverage-renormalized).

Secondary outcomes (frozen):
- dominant replacement (baseline argmax crop != endline argmax), binary
- entry count / disappearance count (crop crosses 1% share threshold)
- L1 distance between share vectors
- delta HHI = HHI(endline) - HHI(baseline)
