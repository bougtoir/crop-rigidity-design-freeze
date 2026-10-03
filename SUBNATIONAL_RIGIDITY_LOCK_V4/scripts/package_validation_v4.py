#!/usr/bin/env python3
"""V4 package validation: checksums, CSV schemas, blind-sim rerun,
and a no-real-interaction-fit check."""
import hashlib, subprocess, sys
from pathlib import Path

V4 = Path(__file__).resolve().parents[1]
ANA = V4 / "analysis"
ok = True

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def rec(f): return f.read_text().split()[0]

def check(name, cond):
    global ok
    print(("PASS" if cond else "FAIL"), name)
    ok = ok and cond

s = ANA / "PRIMARY_SUBNATIONAL_SAMPLE_LOCKED_V4.csv"
check("sample sha256", sha(s) == rec(ANA / "PRIMARY_SUBNATIONAL_SAMPLE_LOCKED_V4.sha256"))
y = V4 / "SUBNATIONAL_PRIMARY_ANALYSIS_LOCK_V4.yaml"
check("lock sha256", sha(y) == rec(V4 / "SUBNATIONAL_PRIMARY_ANALYSIS_LOCK_V4.sha256"))

import pandas as pd
for f, cols in [
    ("jsd_marginal_summary_v4.csv", {"N", "mean", "sd", "median", "min", "max"}),
    ("admin_spatial_blocks_v4.csv", {"unit_id", "block_grid10"}),
    ("information_simulation_v4.csv", {"target_jsd_contrast", "latent_b3"}),
    ("spatial_inference_simulation_v4.csv", {"scenario", "method", "type_I"}),
    ("01_EUROPE_ADMIN_EQUIVALENCE.csv", {"country", "one_to_one_equivalent"}),
]:
    d = pd.read_csv(ANA / f)
    check(f"{f} schema", cols <= set(d.columns))

# no bare-NUTS unit ids in strict sample
d = pd.read_csv(s)
check("no non-first-level ids", d.unit_id.str.contains(":").all())

# information sim reproduces byte-identically
before = sha(ANA / "information_simulation_v4.csv")
repo = V4.parents[0]
subprocess.run([sys.executable, str(repo / "scripts" / "information_simulation_v4.py")],
               check=True, cwd=str(repo), capture_output=True)
check("info sim byte-identical", sha(ANA / "information_simulation_v4.csv") == before)

# blindness: grep for real subnational jsd fits in the subnational
# pipeline (national-phase scripts 01-39 are a closed, different unit
# of observation and are excluded from this check)
import re, glob, os
bad = []
for f in glob.glob(str(repo / "scripts" / "*.py")):
    base = os.path.basename(f)
    if re.match(r"^(0[1-9]|[12][0-9]|3[0-9])_", base):
        continue  # national phase, archived
    t = Path(f).read_text()
    if re.search(r"lstsq\(.*jsd|OLS\(.*jsd|GLM\(.*jsd", t):
        bad.append(base)
check("no real subnational jsd fits", not bad)

sys.exit(0 if ok else 1)
