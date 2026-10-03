#!/usr/bin/env python3
"""V4 strict sample: drop non-equivalent Eurostat NUTS2 units.

Strict primary geography = documented first-level administrative units
only (GADM ADM1, HarvestStat admin_1, US state, Canadian province,
Brazilian UF). Eurostat NUTS2 units are statistical regions — removed
from primary, held as the prespecified NUTS2 sensitivity set.

Emits (in SUBNATIONAL_RIGIDITY_LOCK_V4/analysis/):
  01_EUROPE_ADMIN_EQUIVALENCE.csv
  PRIMARY_SUBNATIONAL_SAMPLE_LOCKED_V4.csv (+ .sha256)
  jsd_marginal_summary_v4.csv
"""
import hashlib
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
V4 = ROOT / "SUBNATIONAL_RIGIDITY_LOCK_V4"
d = pd.read_csv(ROOT / "SUBNATIONAL_RIGIDITY_LOCK_V3" / "analysis"
                / "PRIMARY_SUBNATIONAL_SAMPLE_LOCKED.csv")

eq = [
    ("CH", "NUTS2", "grossregionen (7 statistical regions)",
     "cantons (NUTS3)",
     "Eurostat NUTS2021 correspondence: CH admin-1 = canton"),
    ("EL", "NUTS2", "statistical regions (EL11..EL25, EL3x..EL6x)",
     "periphereies (13, NUTS3)",
     "Eurostat correspondence: EL admin-1 = periphereia"),
    ("HR", "NUTS2", "statistical regions (HR02, HR03...)",
     "21 zupanije (NUTS3)",
     "Eurostat correspondence: HR admin-1 = zupanija"),
    ("IE", "NUTS2", "IE01/IE02 statistical groupings",
     "26 counties + cities",
     "Eurostat correspondence: IE admin-1 = county"),
    ("PT", "NUTS2", "7 statistical regioes",
     "18 districts + 2 autonomous regions (NUTS3)",
     "Eurostat correspondence: PT admin-1 = distrito"),
]
pd.DataFrame(eq, columns=["country", "nuts_level", "nuts_unit",
                          "actual_first_admin_level",
                          "evidence"]).assign(
    one_to_one_equivalent="NO", primary_eligible="NO").to_csv(
    V4 / "analysis" / "01_EUROPE_ADMIN_EQUIVALENCE.csv", index=False)

strict = d[d.unit_id.str.contains(":")].copy()
cnt = strict.country.value_counts()
strict = strict[strict.country.isin(cnt[cnt >= 2].index)]
out = V4 / "analysis" / "PRIMARY_SUBNATIONAL_SAMPLE_LOCKED_V4.csv"
strict.to_csv(out, index=False)
h = hashlib.sha256(out.read_bytes()).hexdigest()
(V4 / "analysis" / "PRIMARY_SUBNATIONAL_SAMPLE_LOCKED_V4.sha256").write_text(
    f"{h}  PRIMARY_SUBNATIONAL_SAMPLE_LOCKED_V4.csv\n")

s = strict.jsd
pd.DataFrame([dict(N=len(s), mean=s.mean(), sd=s.std(), median=s.median(),
                   iqr=s.quantile(.75) - s.quantile(.25), min=s.min(),
                   max=s.max(), frac_zero=(s == 0).mean(),
                   frac_max=(s >= 1 - 1e-9).mean())]).to_csv(
    V4 / "analysis" / "jsd_marginal_summary_v4.csv", index=False)
print(len(strict), strict.country.nunique())
