#!/usr/bin/env python3
"""24_falsification_subgroups.py — falsification suite, leave-one-out,
exploratory subgroups."""
import gzip
import json
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm

ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "CROP_RIGIDITY_PRIMARY_RESULTS"
AN = PKG / "analysis"
LOCK = ROOT / "CROP_RIGIDITY_FINAL_LOCK"
REPAIR = ROOT / "CROP_RIGIDITY_PREANALYSIS_REPAIR"
RAW = ROOT / "data" / "raw"
JSD_MAX = float(np.sqrt(np.log(2)))
rng = np.random.default_rng(20261003)
B = 999

est = pd.read_parquet(PKG / "_cache_est.parquet")
aux = pd.read_csv(AN / "aux_mismatches.csv")
auxv = {k: v.set_index("iso3").mismatch for k, v in aux.groupby("variant")}
xw = pd.read_csv(REPAIR / "COUNTRY_REGION_CROSSWALK.csv")
iso_of = dict(zip(xw.faostat_country, xw.iso3))
sub_of = dict(zip(xw.iso3, xw.subregion))
reg_of = dict(zip(xw.iso3, xw.region))

df = pd.read_feather(RAW / "faostat_qcl_2026-02-25.feather")
audit = pd.read_csv(REPAIR / "FAOSTAT_CROP_ITEM_AUDIT.csv")
keep = set(audit.loc[audit.include_primary == 1, "item_name"])
haf = df[(df.element == "Area harvested") & (df.value > 0)]
haf = haf[haf["item"].isin(keep)][["country", "year", "item", "value"]]

def shares(d):
    s = d.groupby(["country", "item"], observed=True)["value"].mean().reset_index()
    s["share"] = s.value / s.groupby("country", observed=True).value.transform("sum")
    return s

def js(p, q):
    m = 0.5 * (p + q)
    return float(np.sqrt(0.5 * np.where(p > 0, p * np.log(p / m), 0).sum()
                         + 0.5 * np.where(q > 0, q * np.log(q / m), 0).sum()))

def cropmix(leg, out):
    recs = []
    for c, g in haf.groupby("country", observed=True):
        gl = g[(g.year >= leg[0]) & (g.year <= leg[1])]
        go = g[(g.year >= out[0]) & (g.year <= out[1])]
        if gl.year.nunique() < 5 or go.year.nunique() < 5:
            continue
        sl, so = shares(gl), shares(go)
        if sl.item.nunique() < 4 or so.item.nunique() < 4:
            continue
        p = sl.set_index("item")["share"]; q = so.set_index("item")["share"]
        idx = sorted(set(p.index) | set(q.index))
        p, q = p.reindex(idx, fill_value=0.), q.reindex(idx, fill_value=0.)
        recs.append(dict(country=c, hhi=float((p ** 2).sum()),
                         dominant_crop=p.idxmax(), n_years=int(gl.year.nunique()),
                         jsd=js(p.values, q.values)))
    return pd.DataFrame(recs)

def fit_b3(d, hhi_col, m_col, y_col, gids=None, Bn=999):
    d = d.dropna(subset=[hhi_col, m_col, y_col]).copy()
    if len(d) < 20: return dict(n=len(d), beta3=np.nan, lo=np.nan, hi=np.nan)
    hz = (d[hhi_col] - d[hhi_col].mean()) / d[hhi_col].std()
    mz = (d[m_col] - d[m_col].mean()) / d[m_col].std()
    Xd = np.column_stack([np.ones(len(d)), hz, mz, hz * mz])
    yv = np.clip(d[y_col].values / JSD_MAX, 1e-6, 1 - 1e-6)
    try:
        f = sm.GLM(yv, Xd, family=sm.families.Binomial()).fit()
        b3 = float(f.params[3])
    except Exception:
        return dict(n=len(d), beta3=np.nan, lo=np.nan, hi=np.nan)
    g = d.subregion.values if gids is None else gids
    ids = np.unique(g); bs = []
    for _ in range(Bn):
        dr = rng.choice(ids, size=len(ids), replace=True)
        idx = np.concatenate([np.flatnonzero(g == gg) for gg in dr])
        try:
            fb = sm.GLM(yv[idx], Xd[idx], family=sm.families.Binomial()
                        ).fit(disp=0, maxiter=40)
            bs.append(fb.params[3])
        except Exception:
            continue
    bs = np.sort(bs)
    return dict(n=len(d), beta3=b3, lo=float(bs[int(.025*len(bs))]),
                hi=float(bs[int(.975*len(bs))-1]), reps=len(bs))

base = est.copy()
base["jsd_raw"] = base.jsd
res = []

def add(test, kind, r, detail=""):
    res.append(dict(test=test, kind=kind, n=r.get("n"), beta3=r.get("beta3"),
                    ci_lo=r.get("lo"), ci_hi=r.get("hi"), detail=detail))

# F1 future exposure vs PRIOR transformation (outcome 1981-2001 -> 2002-2010)
cm_short = cropmix((1981, 2001), (2002, 2010))
d = base[["country","hhi","subregion"]].merge(
    cm_short[["country","jsd"]].rename(columns={"jsd":"jsd_raw"}), on="country")
d["expo"] = d.country.map(iso_of).map(auxv["future"])
add("F1 future exposure -> prior transformation", "falsification",
    fit_b3(d, "hhi", "expo", "jsd_raw"), "expect ~0")

# F2 pre-treatment 'exposure' window vs frozen outcome
d = base.copy(); d["expo"] = d.iso3.map(auxv["pre_treatment"])
add("F2 wrong temporal exposure window", "falsification",
    fit_b3(d, "hhi", "expo", "jsd_raw"), "expect ~0")

# F3 geographically displaced exposure (region-preserving permutation)
d = base.copy(); d["expo"] = np.nan
okm = auxv["primary"].dropna()
perm_b3 = []
for i in range(200):
    shuffled = pd.Series(rng.permutation(okm.values), index=okm.index)
    # displace: country gets mismatch of a country in a DIFFERENT region
    for iso in base.iso3:
        reg = reg_of.get(iso)
        cand = shuffled[[r for r in shuffled.index if reg_of.get(r) != reg]]
        d.loc[d.iso3 == iso, "expo"] = (
            cand.iloc[rng.integers(len(cand))] if len(cand) else np.nan)
    try:
        hz = (d.hhi - d.hhi.mean()) / d.hhi.std()
        mz = (d.expo - d.expo.mean()) / d.expo.std()
        Xd = np.column_stack([np.ones(len(d)), hz, mz, hz*mz])
        yv = np.clip(d.jsd.values / JSD_MAX, 1e-6, 1-1e-6)
        perm_b3.append(sm.GLM(yv, Xd, family=sm.families.Binomial()
                              ).fit().params[3])
    except Exception:
        pass
perm_b3 = np.array(perm_b3)
add("F3 geographically displaced exposure (200 perm)",
    "falsification",
    dict(n=len(d), beta3=float(np.nanmedian(perm_b3)),
         lo=float(np.nanpercentile(perm_b3, 2.5)),
         hi=float(np.nanpercentile(perm_b3, 97.5))),
    "median permuted beta3 vs primary 0.0046")

# F4 leave-one-region-out
loro = []
for r_ in sorted(base.region.unique()):
    d = base[base.region != r_]
    rr = fit_b3(d.rename(columns={"mismatch": "expo"}), "hhi", "expo", "jsd", Bn=499)
    loro.append(dict(dropped=r_, n=rr["n"], beta3=rr["beta3"],
                     ci_lo=rr["lo"], ci_hi=rr["hi"]))
pd.DataFrame(loro).to_csv(AN / "leave_region_out.csv", index=False)
loro_df = pd.DataFrame(loro)
add("F4 leave-one-region-out range", "falsification",
    dict(n=None, beta3=None, lo=float(loro_df.beta3.min()),
         hi=float(loro_df.beta3.max())),
    f"beta3 in [{loro_df.beta3.min():.3f},{loro_df.beta3.max():.3f}]")

# F5 leave-one-subregion-out
loso = []
for s_ in sorted(base.subregion.unique()):
    d = base[base.subregion != s_]
    rr = fit_b3(d.rename(columns={"mismatch": "expo"}), "hhi", "expo", "jsd", Bn=499)
    loso.append(dict(dropped=s_, n=rr["n"], beta3=rr["beta3"],
                     ci_lo=rr["lo"], ci_hi=rr["hi"]))
pd.DataFrame(loso).to_csv(AN / "leave_subregion_out.csv", index=False)
loso_df = pd.DataFrame(loso)
add("F5 leave-one-subregion-out range", "falsification",
    dict(n=None, beta3=None, lo=float(loso_df.beta3.min()),
         hi=float(loso_df.beta3.max())),
    f"beta3 in [{loso_df.beta3.min():.3f},{loso_df.beta3.max():.3f}]")

# F6 alternate crop set: exclude catch-all OTHE-dominant countries
d = base[base.spam_crop != "OTHE"]
add("F6 exclude OTHE-dominant (residual class)", "falsification",
    fit_b3(d.rename(columns={"mismatch": "expo"}), "hhi", "expo", "jsd_raw"),
    f"n={len(d)}")

# F7 sparse-reporting exclusion: need n_years in frozen window -> compute
cm_fr = cropmix((1981, 2001), (2002, 2020))
ny = dict(zip(cm_fr.country, cm_fr.n_years))
d = base.copy(); d["ny"] = d.country.map(ny)
d2 = d[d.ny >= 15]
add("F7 exclude <15y legacy reporting", "falsification",
    fit_b3(d2.rename(columns={"mismatch": "expo"}), "hhi", "expo", "jsd_raw"),
    f"n={len(d2)}")

# F8 missingness comparison (excluded vs included)
dropped = pd.read_csv(LOCK / "analysis" / "primary_sample_preoutcome.csv")
excl = dropped[~dropped.country.isin(set(est.country))].dropna(
    subset=["hhi", "jsd"])
comp = dict(hhi_in=float(est.hhi.mean()), hhi_out=float(excl.hhi.mean()),
            jsd_in=float(est.jsd.mean()), jsd_out=float(excl.jsd.mean()),
            n_in=len(est), n_out=len(excl))
res.append(dict(test="F8 missingness covariate comparison", kind="audit",
                n=None, beta3=np.nan, ci_lo=np.nan, ci_hi=np.nan,
                detail=json.dumps(comp)))

# F9 pre-trend: transformation between two pre-treatment windows vs mismatch
cm_pt = cropmix((1981, 1990), (1991, 2001))
d = base[["country", "hhi", "mismatch", "subregion"]].merge(
    cm_pt[["country", "jsd"]].rename(columns={"jsd": "jsd_raw"}), on="country")
add("F9 pre-trend (1981-90 -> 1991-01 JSD vs mismatch)", "falsification",
    fit_b3(d.rename(columns={"mismatch": "expo"}), "hhi", "expo", "jsd_raw"),
    "expect ~0")

# F10 permutation preserving design (permute mismatch across countries)
b3_real = float(sm.GLM(np.clip(base.jsd.values / JSD_MAX, 1e-6, 1-1e-6),
                np.column_stack([np.ones(len(base)),
                                 (base.hhi-base.hhi.mean())/base.hhi.std(),
                                 (base.mismatch-base.mismatch.mean())/base.mismatch.std(),
                                 (base.hhi-base.hhi.mean())/base.hhi.std()
                                 * (base.mismatch-base.mismatch.mean())/base.mismatch.std()]),
                family=sm.families.Binomial()).fit().params[3])
pb = []
mv = base.mismatch.values
for _ in range(500):
    mp = rng.permutation(mv)
    hz = (base.hhi-base.hhi.mean())/base.hhi.std()
    mz = (mp-mp.mean())/mp.std()
    Xd = np.column_stack([np.ones(len(base)), hz, mz, hz*mz])
    yv = np.clip(base.jsd.values/JSD_MAX, 1e-6, 1-1e-6)
    try:
        pb.append(sm.GLM(yv, Xd, family=sm.families.Binomial()).fit().params[3])
    except Exception:
        pass
pb = np.array(pb)
res.append(dict(test="F10 null permutation (500)", kind="falsification",
                n=len(base), beta3=b3_real,
                ci_lo=float(np.percentile(pb, 2.5)),
                ci_hi=float(np.percentile(pb, 97.5)),
                detail=f"permuted 95% range [{np.percentile(pb,2.5):.3f},{np.percentile(pb,97.5):.3f}]; real {b3_real:.3f} inside"))

pd.DataFrame(res).to_csv(AN / "falsification_results.csv", index=False)
print(pd.DataFrame(res)[["test", "beta3", "ci_lo", "ci_hi", "detail"]]
      .to_string(index=False))

# ---------------- exploratory subgroups -------------------------------------
# irrigation share of dominant crop via MIRCA CCC areas
def parse_ccc_areas(path):
    out = {}
    with gzip.open(path, "rt") as f:
        for line in f:
            t = line.split()
            if len(t) < 3 or not t[0].lstrip("-").isdigit():
                continue
            u, c, n = int(t[0]), int(t[1]), int(t[2]); area = 0.0
            for k in range(min(n, 5)):
                j = 3 + k * 3
                if j + 2 < len(t):
                    try: area += float(t[j])
                    except ValueError: pass
            out.setdefault(u, {})[c] = out.setdefault(u, {}).get(c, 0.) + area
    return out

cc = RAW / "mirca" / "condensed_cropping_calendars"
ar_i = parse_ccc_areas(cc / "cropping_calendar_irrigated.txt.gz")
ar_r = parse_ccc_areas(cc / "cropping_calendar_rainfed.txt.gz")
SPAM2MIRCA = {"WHEA": [1], "MAIZ": [2], "RICE": [3], "BARL": [4], "MILL": [6],
              "SORG": [7], "SOYB": [8], "POTA": [10], "CASS": [11],
              "SUGC": [12], "SUGB": [13], "OPUL": [17], "BEAN": [17],
              "GROU": [16], "COTT": [21], "COFF": [23], "SWPY": [26],
              "BANP": [26], "OFIB": [26], "OOIL": [8, 9, 14, 15, 24],
              "OTHE": [24, 26]}
# cell->unit from footprint of the dominant crop
fc = pd.read_csv(REPAIR / "analysis" / "footprint_cells.csv")
hdr = {}
with open(RAW / "mirca" / "unit_code_grid" / "unit_code.asc") as f:
    for _ in range(6):
        k, v = f.readline().split(); hdr[k.lower()] = float(v)
    grid = np.loadtxt(f)
CS = hdr["cellsize"]
def unit_at(lon, lat):
    col = min(max(int((lon+180)/CS), 0), grid.shape[1]-1)
    row = min(max(int((90-lat)/CS), 0), grid.shape[0]-1)
    if grid[row, col] != -9999: return int(grid[row, col])
    for rad in (2, 4, 8, 16):
        vals = grid[max(0, row-rad):row+rad+1, max(0, col-rad):col+rad+1]
        ok = vals[vals != -9999]
        if ok.size:
            u, c = np.unique(ok.astype(int), return_counts=True)
            return int(u[c.argmax()])
    return -9999

irr_share = {}
for _, r in est.iterrows():
    rows = fc[(fc.iso3 == r.iso3) & (fc.spam_crop == r.spam_crop)]
    if rows.empty: continue
    cells = set()
    for j in rows.cells_json:
        cells.update(map(tuple, json.loads(j)))
    units = {unit_at(*c) for c in cells}
    ai = ar = 0.0
    for u in units:
        for cl in SPAM2MIRCA.get(r.spam_crop, []):
            ai += ar_i.get(u, {}).get(cl, 0.)
            ar += ar_r.get(u, {}).get(cl, 0.)
    if ai + ar > 0:
        irr_share[r.iso3] = ai / (ai + ar)
base["irr_share"] = base.iso3.map(irr_share)
CEREALS = {"WHEA", "RICE", "MAIZ", "BARL", "MILL", "SORG"}
sgr = []
for dim, m in [("tropical |lat|<=23.5", base.centroid_lat.abs() <= 23.5),
               ("nontropical", base.centroid_lat.abs() > 23.5),
               ("cereal-dominant", base.spam_crop.isin(CEREALS)),
               ("noncereal-dominant", ~base.spam_crop.isin(CEREALS)),
               ("high irrigation", base.irr_share >= base.irr_share.median()),
               ("low irrigation", base.irr_share < base.irr_share.median())]:
    d = base[m].rename(columns={"mismatch": "expo"})
    r = fit_b3(d, "hhi", "expo", "jsd_raw", Bn=499)
    sgr.append(dict(subgroup=dim, n=r["n"], beta3=r["beta3"],
                    ci_lo=r["lo"], ci_hi=r["hi"], note="exploratory"))
for rg in sorted(base.region.unique()):
    d = base[base.region == rg].rename(columns={"mismatch": "expo"})
    r = fit_b3(d, "hhi", "expo", "jsd_raw", Bn=499)
    sgr.append(dict(subgroup=f"region {rg}", n=r["n"], beta3=r["beta3"],
                    ci_lo=r["lo"], ci_hi=r["hi"], note="exploratory"))
pd.DataFrame(sgr).to_csv(AN / "subgroup_exploratory_results.csv", index=False)
print(pd.DataFrame(sgr).to_string(index=False))
