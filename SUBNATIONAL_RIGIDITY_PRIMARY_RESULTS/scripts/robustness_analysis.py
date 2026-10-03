#!/usr/bin/env python3
"""Prespecified robustness + secondary exposures + LOCO/LORO.

Every analysis records one interaction estimate into
analysis/ROBUSTNESS_LEDGER.csv. Secondary exposures (HHI, perennial)
go to analysis/secondary_exposure_results.csv.
"""
import sys
import numpy as np
import pandas as pd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from pipeline_common import (ANA, V3, SEED, verify_lock, load_sample,
                             design, ols, block_boot_est, fit_all)

verify_lock()
dm = load_sample()
y = dm.jsd.values
I = dm.irr_share_base2000.values
M = dm.mismatch_T.values
I75, I25 = np.quantile(I, [.75, .25])
sdM = M.std(ddof=1)
rows = []


def bboot_ci(boot_col, idx=3):
    X_, _ = design(dm)
    bs = block_boot_est(dm, X_, y, boot_col, B=999, seed=SEED)
    e = bs[:, idx]
    return float(np.quantile(e, .025)), float(np.quantile(e, .975)), \
        float(2 * min((e <= 0).mean(), (e >= 0).mean()))


def rec(aid, kind, dd, irr, mm, model, est, lo, hi, p, notes=""):
    rows.append(dict(analysis_id=aid, primary_or_secondary=kind,
                     N=len(dd), countries=dd.country.nunique(),
                     outcome="jsd", exposure=irr, mismatch=mm,
                     model=model, interaction_estimate=est,
                     CI_low=lo, CI_high=hi, p_value=p,
                     direction=np.sign(est), notes=notes))


# R0 primary (reference)
X, _ = design(dm)
b, _ = ols(X, y)
lo, hi, p = bboot_ci("block_grid10")
rec("primary_OLS_grid10", "primary", dm, "irr_share_base2000",
    "mismatch_T", "OLS+countryFE", b[3], lo, hi, p)

# R1 fractional-logit GLM
bf, _ = fit_all(dm, frac=True)
rec("frac_logit_GLM", "primary", dm, "irr_share_base2000",
    "mismatch_T", "fractional logit GLM+countryFE", float(bf[3]),
    np.nan, np.nan, np.nan, "point estimate only (link scale)")

# R2 grid15 / R3 kmeans blocks
b2, _ = ols(X, y)
lo, hi, p = bboot_ci("block_grid15")
rec("OLS_grid15", "primary", dm, "irr_share_base2000", "mismatch_T",
    "OLS+countryFE, grid15 blocks", b2[3], lo, hi, p)
lo, hi, p = bboot_ci("block_km")
rec("OLS_kmeans", "primary", dm, "irr_share_base2000", "mismatch_T",
    "OLS+countryFE, within-country kmeans blocks", b2[3], lo, hi, p)

# R4 SPAM2010 irrigation (rows with non-null SPAM2010 share)
d4 = dm.dropna(subset=["irr_share_spam"])
X4, _ = design(d4, "irr_share_spam")
b4, _ = ols(X4, d4.jsd.values)
bs4 = block_boot_est(d4, X4, d4.jsd.values, "block_grid10",
                     B=999, seed=SEED)[:, 3]
rec("OLS_irr_spam2010", "primary", d4, "irr_share_spam", "mismatch_T",
    "OLS+countryFE", b4[3], *np.quantile(bs4, [.025, .975]),
    float(2 * min((bs4 <= 0).mean(), (bs4 >= 0).mean())),
    notes=f"N={len(d4)} after dropping 26 null SPAM2010 shares")

# R5 NUTS2 sensitivity sample (V3 strict-including set)
dv3 = pd.read_csv(V3 / "analysis" / "PRIMARY_SUBNATIONAL_SAMPLE_LOCKED.csv")
dv3 = dv3.merge(dm[["unit_id"]].assign(_in=1), on="unit_id", how="left")
# rebuild design on the V3 rows that survive missingness
dv3 = dv3.dropna(subset=["jsd", "irr_share_base2000", "mismatch_T"])
Xv, _ = design(dv3)
bv, _ = ols(Xv, dv3.jsd.values)
# block bootstrap needs block ids; reuse grid10 formula on centroids
blkv = pd.read_csv(V3 / "analysis" / "admin_spatial_blocks_v3.csv")
dv3 = dv3.merge(blkv[["unit_id", "block_grid10"]], on="unit_id")
bsv = block_boot_est(dv3, Xv, dv3.jsd.values, "block_grid10",
                     B=999, seed=SEED)[:, 3]
rec("OLS_NUTS2_sensitivity", "primary", dv3, "irr_share_base2000",
    "mismatch_T", "OLS+countryFE on V3 sample (incl 33 NUTS2)",
    bv[3], *np.quantile(bsv, [.025, .975]),
    float(2 * min((bsv <= 0).mean(), (bsv >= 0).mean())),
    notes=f"N={len(dv3)}")

# R6 HHI mechanism-control
X6, _ = design(dm, extra=["hhi_baseline"])
b6, _ = ols(X6, y)
bs6 = block_boot_est(dm, X6, y, "block_grid10", B=999, seed=SEED)[:, 3]
rec("OLS_HHI_control", "primary", dm, "irr_share_base2000",
    "mismatch_T", "OLS+countryFE+hhi_baseline", b6[3],
    *np.quantile(bs6, [.025, .975]),
    float(2 * min((bs6 <= 0).mean(), (bs6 >= 0).mean())))

# R7 baseline area precision control
dl = dm.assign(log_area=np.log(dm.area_baseline.clip(lower=1)))
X7 = np.c_[design(dl)[0], np.log(dm.area_baseline.clip(lower=1)).values]
b7, _ = ols(X7, y)
bs7 = block_boot_est(dm, X7, y, "block_grid10", B=999, seed=SEED)[:, 3]
rec("OLS_area_precision", "primary", dm, "irr_share_base2000",
    "mismatch_T", "OLS+countryFE+log(area_baseline)", b7[3],
    *np.quantile(bs7, [.025, .975]),
    float(2 * min((bs7 <= 0).mean(), (bs7 >= 0).mean())))

# R8 perennial-strict secondary exposure (also reported in secondary file)
Xp = np.c_[np.ones(len(dm)), dm.perennial_strict.values,
           dm.mismatch_T.values,
           dm.perennial_strict.values * dm.mismatch_T.values,
           pd.get_dummies(dm.country, drop_first=True).values.astype(float)]
bp, _ = ols(Xp, y)
bsp = block_boot_est(dm, Xp, y, "block_grid10", B=999, seed=SEED)[:, 3]
rec("OLS_perennial_strict", "secondary", dm, "perennial_strict",
    "mismatch_T", "OLS+countryFE", bp[3], *np.quantile(bsp, [.025, .975]),
    float(2 * min((bsp <= 0).mean(), (bsp >= 0).mean())))

# R9 leave-one-country-out
loco = []
for c in sorted(dm.country.unique()):
    dd = dm[dm.country != c]
    Xc, _ = design(dd)
    bc, _ = ols(Xc, dd.jsd.values)
    loco.append(dict(dropped_country=c, N=len(dd), beta3=bc[3]))
pd.DataFrame(loco).to_csv(ANA / "leave_one_country_out.csv", index=False)
lr = pd.DataFrame(loco)
rec("LOCO_range", "primary", dm, "irr_share_base2000", "mismatch_T",
    "OLS+countryFE, leave-one-country-out", np.nan,
    lr.beta3.min(), lr.beta3.max(), np.nan,
    notes=f"beta3 range [{lr.beta3.min():.4f},{lr.beta3.max():.4f}]")

# R10 leave-one-region-out
SSA = {"Angola", "Benin", "Burkina Faso", "Chad", "Ethiopia", "Ghana",
       "Lesotho", "Malawi", "Mali", "Mauritania", "Mozambique", "Niger",
       "Nigeria", "Senegal", "South Africa", "Sudan",
       "Tanzania, United Republic of", "Zambia"}
def region(c):
    if c in SSA: return "SSA"
    if c in {"United States", "Canada"}: return "NAm"
    if c == "Brazil": return "LAm"
    return "Asia"
dmr = dm.assign(region=dm.country.map(region))
loro = []
for r in sorted(dmr.region.unique()):
    dd = dmr[dmr.region != r]
    Xr, _ = design(dd)
    br, _ = ols(Xr, dd.jsd.values)
    loro.append(dict(dropped_region=r, N=len(dd),
                     countries=dd.country.nunique(), beta3=br[3]))
pd.DataFrame(loro).to_csv(ANA / "leave_one_region_out.csv", index=False)
lrr = pd.DataFrame(loro)
rec("LORO_range", "primary", dm, "irr_share_base2000", "mismatch_T",
    "OLS+countryFE, leave-one-region-out", np.nan,
    lrr.beta3.min(), lrr.beta3.max(), np.nan,
    notes=f"beta3 range [{lrr.beta3.min():.4f},{lrr.beta3.max():.4f}]")

pd.DataFrame(rows).to_csv(ANA / "ROBUSTNESS_LEDGER.csv", index=False)

# ---- secondary exposures file ----
sec = []
Xh = np.c_[np.ones(len(dm)), dm.hhi_baseline.values,
           dm.mismatch_T.values,
           dm.hhi_baseline.values * dm.mismatch_T.values,
           pd.get_dummies(dm.country, drop_first=True).values.astype(float)]
bh, _ = ols(Xh, y)
bsh = block_boot_est(dm, Xh, y, "block_grid10", B=999, seed=SEED)[:, 3]
sec.append(dict(hypothesis="H_HHI", exposure="hhi_baseline",
                interaction=bh[3], ci_lo=np.quantile(bsh, .025),
                ci_hi=np.quantile(bsh, .975),
                p=2 * min((bsh <= 0).mean(), (bsh >= 0).mean())))
sec.append(dict(hypothesis="H_PERENNIAL", exposure="perennial_strict",
                interaction=bp[3], ci_lo=np.quantile(bsp, .025),
                ci_hi=np.quantile(bsp, .975),
                p=2 * min((bsp <= 0).mean(), (bsp >= 0).mean())))
pd.DataFrame(sec).to_csv(ANA / "secondary_exposure_results.csv",
                         index=False)
print(pd.DataFrame(rows).round(4).to_string(index=False))
print(pd.DataFrame(sec).round(4).to_string(index=False))
