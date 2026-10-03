#!/usr/bin/env python3
"""Prespecified falsification suite — analysis/falsification_results.csv.

Each row: interaction estimate of the frozen OLS form under a
deliberately wrong or alternative specification. Pre-registered vs
post-hoc flagged per test.
"""
import sys
import numpy as np
import pandas as pd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from pipeline_common import (ANA, SEED, verify_lock, load_sample,
                             ols, block_boot_est)

verify_lock()
dm = load_sample()
y = dm.jsd.values
FE = pd.get_dummies(dm.country, drop_first=True).values.astype(float)
rows = []


def Xf(dd, irr, mm):
    fe = pd.get_dummies(dd.country, drop_first=True).values.astype(float)
    return np.c_[np.ones(len(dd)), irr, mm, irr * mm, fe]


def b3(dd, irr, mm):
    X = Xf(dd, irr(dd), mm(dd))
    b, _ = ols(X, dd.jsd.values)
    bs = block_boot_est(dd, X, dd.jsd.values, "block_grid10",
                        B=999, seed=SEED)[:, 3]
    return b[3], *np.quantile(bs, [.025, .975]), \
        float(2 * min((bs <= 0).mean(), (bs >= 0).mean()))


def rec(tid, name, est, lo, hi, p, prereg, notes=""):
    rows.append(dict(test_id=tid, test=name, interaction=est,
                     ci_lo=lo, ci_hi=hi, p_value=p,
                     pre_or_post=prereg, notes=notes))


# F1 wrong climate variable (precipitation mismatch)
d = dm.dropna(subset=["mismatch_P"])
rec("F1_wrong_climate", "precipitation mismatch substituted for thermal",
    *b3(d, lambda x: x.irr_share_base2000.values, lambda x: x.mismatch_P.values),
    "pre", f"N={len(d)}")

# F2 spatially shifted mismatch (rotate within country by 1 unit)
def shifted(dd):
    out = dd.copy()
    out["mm_sh"] = np.nan
    for c, g in dd.groupby("country"):
        g = g.sort_values("lat")
        v = g.mismatch_T.values
        out.loc[g.index, "mm_sh"] = np.roll(v, 1)
    return out.mm_sh.fillna(out.mismatch_T).values
rec("F2_spatial_shift", "mismatch shifted to neighbouring unit",
    *b3(dm, lambda x: x.irr_share_base2000.values, shifted), "pre")

# F3 alternative irrigation source (MIRCA2000)
d = dm.dropna(subset=["irr_share_mirca"])
rec("F3_alt_irrigation", "MIRCA2000 irrigation share",
    *b3(d, lambda x: x.irr_share_mirca.values, lambda x: x.mismatch_T.values),
    "pre", f"N={len(d)}")

# F4 sparse-reporting exclusion (n_crops_b >= country median)
d = dm[dm.n_crops_b >= dm.groupby("country").n_crops_b.transform("median")]
rec("F4_sparse_excl", "exclude below-median crop-reporting units",
    *b3(d, lambda x: x.irr_share_base2000.values, lambda x: x.mismatch_T.values),
    "post", f"N={len(d)}")

# F5 alternative window proxy: outcome vs baseline L1 (wrong outcome)
# use L1 distance as outcome (different transformation metric)
X = Xf(dm, dm.irr_share_base2000.values, dm.mismatch_T.values)
b, _ = ols(X, dm.l1.values)
bs = block_boot_est(dm, X, dm.l1.values, "block_grid10",
                    B=999, seed=SEED)[:, 3]
rec("F5_alt_outcome_metric", "L1 outcome instead of JSD",
    b[3], *np.quantile(bs, [.025, .975]),
    float(2 * min((bs <= 0).mean(), (bs >= 0).mean())), "post")

# F6 null spatial permutation: shuffle mismatch across blocks, 999x
rng = np.random.default_rng(SEED)
X0 = Xf(dm, dm.irr_share_base2000.values, dm.mismatch_T.values)
b_obs = ols(X0, y)[0][3]
cnt = 0
perm_b3 = []
mmv = dm.mismatch_T.values.copy()
for _ in range(999):
    mmp = mmv.copy()
    rng.shuffle(mmp)
    Xp = Xf(dm, dm.irr_share_base2000.values, mmp)
    try:
        perm_b3.append(ols(Xp, y)[0][3])
    except Exception:
        pass
perm_b3 = np.array(perm_b3)
rec("F6_null_permutation", "mismatch permuted across all units (999x)",
    float(perm_b3.mean()), *np.quantile(perm_b3, [.025, .975]),
    float((np.abs(perm_b3) >= abs(b_obs)).mean()), "pre",
    notes=f"observed b3={b_obs:.4f}; permuted mean/null-p shown")

# F7 NUTS2 scope already covered in robustness ledger (reference row)
rec("F7_scope", "NUTS2 scope sensitivity - see ROBUSTNESS_LEDGER",
    np.nan, np.nan, np.nan, np.nan, "pre", "deferred to R5")

pd.DataFrame(rows).to_csv(ANA / "falsification_results.csv", index=False)
print(pd.DataFrame(rows).round(4).to_string(index=False))
