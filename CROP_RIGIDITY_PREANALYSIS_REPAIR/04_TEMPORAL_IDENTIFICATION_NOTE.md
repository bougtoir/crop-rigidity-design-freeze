# 04 — Temporal Identification Note

## The overlap, made explicit

The frozen exposure window (climatic mismatch, 2001–2020) and the
frozen outcome window (crop-mix change, 2001–2020) are the **same**
period. This is inherent: the hypothesis asks whether realised
environmental change over a period conditions the crop-mix
transformation realised over that period. The exposure is therefore
not strictly "pre-treatment" relative to the outcome — both are
realisations of the 2001–2020 regime.

What the design does have:

- **Legacy (1981–2000)** is strictly pre-treatment: crop-mix HHI and the
  dominant crop are measured before the exposure/outcome window.
- **Baseline footprint (SPAM 2000)** and **baseline climate niche
  (1984–2000)** are strictly pre-treatment: mismatch is measured as the
  displacement of post-2001 climate *relative to* the pre-2001 niche of
  the pre-2001 crop. The treatment variable contains no post-2001 crop
  allocation.

So the estimand is: does pre-2001 structure (L) moderate the
relationship between post-2001 climatic displacement of the pre-2001
crop's niche (M) and post-2001 mix transformation (Δmix)?

## Lagged sensitivity analysis (pre-specified, secondary)

To address residual concern that within-window dynamics drive both M
and Δmix, a lagged split is defined **before observing β3**:

- Legacy: 1981–2000 (unchanged)
- Exposure: **2001–2010**
- Transformation: **2011–2020**

This splits the shared window so that exposure strictly precedes the
outcome window. It is a **sensitivity analysis, not the primary
specification** — the primary remains the 2001–2020/full-window design.
Under the lagged split the same model, estimand, and inferential
pipeline are used; only the windows differ. Interpretation of the
lagged sensitivity relative to the primary is reserved for the
analysis phase.

## What this design cannot claim

It cannot claim that mismatch precedes transformation within the
primary window. If the β3 signal survives only under the contemporaneous
windows and vanishes under the lagged split, the honest reading is that
the interaction operates through within-period co-movement, not through
a strictly lagged causal channel. Both readings are pre-declared
admissible outcomes.
