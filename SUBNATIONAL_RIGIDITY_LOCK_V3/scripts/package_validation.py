#!/usr/bin/env python3
"""Package validation for SUBNATIONAL_RIGIDITY_LOCK_V3.

Checks:
1. PRIMARY_SUBNATIONAL_SAMPLE_LOCKED.csv matches its .sha256.
2. SUBNATIONAL_PRIMARY_ANALYSIS_LOCK_v3.yaml matches its .sha256.
3. information_simulation_v3 re-run reproduces its CSV byte-identically.
Exits non-zero on any failure.
"""
import hashlib
import subprocess
import sys
from pathlib import Path

V3 = Path(__file__).resolve().parents[1]
ANA = V3 / "analysis"


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def recorded(f):
    return f.read_text().split()[0]


ok = True
sample = ANA / "PRIMARY_SUBNATIONAL_SAMPLE_LOCKED.csv"
if sha(sample) != recorded(ANA / "PRIMARY_SUBNATIONAL_SAMPLE_LOCKED.sha256"):
    print("FAIL: sample checksum mismatch")
    ok = False
else:
    print("PASS: sample checksum")

yaml_ = V3 / "SUBNATIONAL_PRIMARY_ANALYSIS_LOCK_v3.yaml"
if sha(yaml_) != recorded(V3 / "SUBNATIONAL_PRIMARY_ANALYSIS_LOCK_v3.sha256"):
    print("FAIL: lock checksum mismatch")
    ok = False
else:
    print("PASS: lock checksum")

csv = ANA / "information_simulation_v3.csv"
before = sha(csv)
repo = V3.parents[0]
subprocess.run([sys.executable, str(repo / "scripts" /
               "information_simulation_v3.py")], check=True,
               cwd=str(repo), capture_output=True)
if sha(csv) != before:
    print("FAIL: information_simulation_v3.py did not reproduce CSV")
    ok = False
else:
    print("PASS: information_simulation_v3 reproduces CSV")

sys.exit(0 if ok else 1)
