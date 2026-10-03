# 08 — Pilot report (measurement compatibility, no hypothesis test)

Pilot scope: SPAM2005 v3.2 vs SPAM2010 v2.0 harvested-area rasters,
wheat/maize/rice, global. Purpose: quantify whether cross-vintage pixel
differences can serve as a transformation outcome, and at what scale
apparent change persists. Script: `scripts/30_spam_vintage_pilot.py`
(raw numbers in `analysis/spam_vintage_pilot.json`).

## Results

| Crop | pixel corr(05,10) | cells gone | cells new | L1 dissimilarity | national |Δ| (Mha) |
|---|---|---|---|---|---|---|
| wheat | 0.840 | 14.4% | 25.6% | 0.232 | 5.36 |
| maize | 0.787 | 17.5% | 22.4% | 0.273 | 17.97 |
| rice | 0.913 | 24.5% | 21.0% | 0.195 | 7.11 |

## Aggregation attenuation (wheat / maize / rice)

| Scale | L1 | corr | gone | new |
|---|---|---|---|---|
| 5′ pixel | .23 / .27 / .19 | .84 / .79 / .91 | .14 / .18 / .24 | .26 / .22 / .21 |
| 0.5° | .13 / .15 / .10 | .96 / .93 / .98 | .08 / .07 / .13 | .10 / .08 / .09 |
| 1.5° | .09 / .11 / .07 | .98 / .97 / .99 | .06 / .04 / .08 | .07 / .06 / .05 |
| 2.5° | .07 / .09 / .06 | .99 / .99 / 1.00 | .05 / .03 / .06 | .06 / .07 / .07 |

## Interpretation

1. Apparent pixel-level transformation is large but ~half of it
   disappears by 0.5° and ~3/4 by 2.5° — consistent with cross-entropy
   reallocation noise rather than observed movement. **Pixel-level
   cross-vintage outcomes are rejected** (confirms the unit decision).
2. A residual ~6–15% compositional change survives at 0.5–2.5°, i.e.
   there *is* measurable subnational change signal at admin-ish scales.
   At admin level the stats are observations, not allocations.
3. Gross pixel churn (L1 ≈ 0.2) vs national |Δ| (~5 Mha wheat) shows the
   H4 signature empirically: between-location reallocation mass far
   exceeds net national change — the decomposition is non-vacuous.
4. Temporal ordering is valid: vintages 2005→2010; mismatch window
   2002–2020 overlaps the outcome era only partially; baseline exposure
   must use ≤2005 layers — consistent with the frozen boundary rule
   (strict pre-exposure ≤2001 stays the preferred design; 2005-vintage
   exposure would need a shifted lock — flagged for next phase).

## Required next-phase check (not done here)

Harmonized admin coverage audit on GSAP/Agro-MAPS: count of countries
with ≥2 same-method vintages, admin-1 availability, and boundary
stability. This is the binding feasibility constraint.
