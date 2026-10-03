# 09 — Retention-burden counterfactual protocol

Strictly separated from the observational transformation analysis. No
observational estimates enter this module and no counterfactual quantities
enter the regression.

## Definitions

For each spatial unit (country in primary reporting; grid cell in the
MapSPAM validation arm):

    V_retain    = Σ_c s_ic(legacy) × Suitability_c(future)
    V_flexible  = Σ_c s_ic(optimized) × Suitability_c(future)

    RO  = V_flexible − V_retain        (Raw Retention Opportunity)

"Retention Burden" language is used only where RO > 0 materially; otherwise
the quantity is reported as raw substitution opportunity without normative
labelling.

## Suitability source

GAEZ v4 Theme 4 (acquired): RES05-SCI suitability classes and RES05-YLDL
attainable yield, baseline TP-2010 (CRUTS32, high input, irrigated) vs TP-2070
(ENSEMBLE, RCP8.5, no CO2 fertilization), crops WHE/COT/SUC. Coverage note:
the public GCS release mirrors only these 3 crops × 2 periods × this input
scenario — a real limitation recorded in the ledger and at the gate.

Supplementary projection arm: ISIMIP3b LPJmL yieldchange-mai under
GFDL-ESM4 and IPSL-CM6A-LR, SSP585 (both acquired) → satisfies ≥2 GCMs.
Additional SSPs (ssp126/ssp370 LPJmL files exist in the same API tree) are
enumerated for the full run.

## Optimization

s_flexible solves max Σ s_c·Y_c s.t. Σ s_c = 1, s_c ≥ 0, plus an agronomic
cap (no single substitute may exceed the largest observed share of that crop
anywhere in the same agro-climatic zone — prevents degenerate
"everyone grows the best crop" solutions).

## Switching-penalty sensitivity bands (labelled ASSUMPTIONS, not estimates)

    V_flexible_net(s) = V_flexible − s · V_retain ,  s ∈ {0, 0.10, 0.20, 0.30}

Reported as bands, never as a point estimate of social switching cost.

## T* rule

T* = smallest climate displacement (standardized growing-season temperature
shift on the unit's footprint) at which V_flexible − V_retain exceeds the
penalty band edge. If curves never cross inside the analysed range, report
"no crossing in analysed range" — T* is never forced or extrapolated.

## Deliverables of this module (at analysis time)

Per-unit RO under each {GCM × period × SSP} cell; sensitivity bands; T* table;
a map-ready raster stack retained in analysis/ with checksums.
