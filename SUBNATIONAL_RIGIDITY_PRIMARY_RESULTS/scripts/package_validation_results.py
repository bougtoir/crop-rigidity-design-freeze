#!/usr/bin/env python3
"""Validate SUBNATIONAL_RIGIDITY_PRIMARY_RESULTS package."""
import hashlib
import sys
from pathlib import Path

RES = Path(__file__).resolve().parents[1]
ANA = RES / "analysis"
ok = True


def check(name, cond):
    global ok
    print(("PASS" if cond else "FAIL"), name)
    ok = ok and cond


req = [
    "00_LOCK_AND_PATCH_VERIFICATION.md", "01_PRIMARY_FIRST_OPENING.md",
    "02_PRIMARY_INFERENCE.md", "03_PRIMARY_EFFECTS.md",
    "04_ROBUSTNESS_REPORT.md", "05_H4_REALLOCATION_REPORT.md",
    "06_SECONDARY_EXPOSURES.md", "07_FALSIFICATION_REPORT.md",
    "08_RESULT_CLASSIFICATION.md", "09_NATIONAL_SUBNATIONAL_SYNTHESIS.md",
    "10_NATURE_VIABILITY.md", "11_NEXT_PHASE_RECOMMENDATION.md",
    "FINAL_HANDOFF.md", "09_SIMULATION_PATCH_REPORT.md",
    "SUBNATIONAL_PRIMARY_ANALYSIS_LOCK_V4.yaml",
    "SUBNATIONAL_PRIMARY_ANALYSIS_LOCK_V4.sha256",
    "analysis/PRIMARY_SUBNATIONAL_SAMPLE_LOCKED_V4.csv",
    "analysis/PRIMARY_SUBNATIONAL_SAMPLE_LOCKED_V4.sha256",
    "analysis/information_simulation_v4_1.csv",
    "analysis/PRIMARY_FIRST_OPENING_SUBNATIONAL.json",
    "analysis/PRIMARY_FIRST_OPENING_SUBNATIONAL.sha256",
    "analysis/primary_model_results.csv",
    "analysis/primary_block_bootstrap_999.csv",
    "analysis/primary_effects.csv",
    "analysis/ROBUSTNESS_LEDGER.csv",
    "analysis/H4_decomposition_results.csv",
    "analysis/secondary_exposure_results.csv",
    "analysis/falsification_results.csv",
    "analysis/leave_one_country_out.csv",
    "analysis/leave_one_region_out.csv",
    "figures/primary_scatter.png", "figures/primary_predictions.png",
    "figures/marginal_effect_curve.png",
    "figures/primary_effect_forest.png", "figures/H4_decomposition.png",
    "scripts/information_simulation_v4_1.py",
    "scripts/primary_analysis_locked.py", "scripts/robustness_analysis.py",
    "scripts/H4_analysis.py", "scripts/falsification_analysis.py",
    "scripts/package_validation_results.py",
]
for f in req:
    check(f, (RES / f).exists())

import pandas as pd
boot = pd.read_csv(ANA / "primary_block_bootstrap_999.csv")
check("bootstrap B=999", len(boot) == 999)
check("bootstrap cols", {"const", "irr", "mm", "irr_x_mm"}
      <= set(boot.columns))
led = pd.read_csv(ANA / "ROBUSTNESS_LEDGER.csv")
check("ledger >= 10 prespecified analyses", len(led) >= 10)
check("opening sha256 file exists",
      (ANA / "PRIMARY_FIRST_OPENING_SUBNATIONAL.sha256").read_text()
      .split()[0] == hashlib.sha256(
          (ANA / "PRIMARY_FIRST_OPENING_SUBNATIONAL.json")
          .read_bytes()).hexdigest())
h4 = pd.read_csv(ANA / "H4_decomposition_results.csv")
check("H4 exact decomposition", h4.exact_err.abs().max() < 1e-9)

sys.exit(0 if ok else 1)
