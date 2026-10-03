# 02 — Exposure-Level Decision (dominant crop vs portfolio)

## Audit finding

The frozen dominant-crop mismatch could in principle be a selection
artifact: the dominant crop is a single draw from the legacy mix, so the
mismatch measure inherits the portfolio's own concentration. This note
compares the two exposure constructions **without touching the outcome
model**.

## Constructions

- **Dominant**: Mahalanobis displacement of the legacy dominant crop's
  SPAM2000 footprint niche (baseline 1984–2000 vs exposure 2001–2020).
- **Portfolio**: `Σ_c s_ic × Mismatch_ic`, share-weighted over legacy
  (1981–2000) FAOSTAT shares mapped to SPAM classes via
  `SPAM_FAOSTAT_CROSSWALK.csv`.

## Empirical comparison (no outcome used)

From `analysis/portfolio_mismatch_country.csv`:

- Pearson correlation dominant vs portfolio: **0.998** — the two
  measures are effectively collinear on the observed sample.
- Share coverage of the portfolio (fraction of legacy area mapped to a
  SPAM class with a non-missing mismatch): median **0.84**, IQR
  ~0.63–0.92; countries with very low coverage are those whose dominant
  crop is a non-SPAM specialty item (e.g., dates, cocoa in OTHE) or
  small islands without POWER coverage.
- Countries where the two measures disagree (portfolio − dominant
  residual > 1 SD): a small set concentrated in low-coverage,
  high-diversity portfolios — exactly where HHI is low, so the dominant
  crop is less representative.

## Dependence on HHI

By construction, dominant and portfolio diverge only when HHI is low:
in high-concentration countries the portfolio is dominated by the
dominant crop anyway. The observed |portfolio − dominant| gap is a
decreasing function of legacy HHI — the dominant-crop measure is
degenerate-in-concentration, not arbitrary.

## Decision (conceptual, pre-registered logic)

**Primary exposure stays dominant-crop mismatch**; portfolio mismatch
is the pre-specified robustness alternative in the multiverse. Rationale:

1. The dominant-crop choice is defined by the legacy mix alone and is
   therefore exogenous to post-2001 outcomes.
2. At 0.998 correlation, switching cannot materially change β3 —
   the decision is conceptually, not empirically, load-bearing.
3. Missingness differs: portfolio adds coverage where the dominant
   crop has a SPAM class but thin footprint; dominant is simpler to
   interpret as "the climate niche of the crop the country actually
   depends on."

This decision was taken before any β3 estimation, as required.
