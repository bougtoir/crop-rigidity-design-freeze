#!/usr/bin/env python3
"""05_validate_manifest.py — verify every file in PACKAGE_MANIFEST.csv exists
in the package and that no unlisted files were added silently.
Exit 0 on consistency, 1 otherwise."""
import sys
from pathlib import Path

import pandas as pd

_here = Path(__file__).resolve()
PKG = _here.parents[1] / "CROP_RIGIDITY_FINAL_LOCK"
if not (PKG / "PACKAGE_MANIFEST.csv").exists():
    # script lives inside the package's scripts/ dir
    PKG = _here.parents[1]
mf = pd.read_csv(PKG / "PACKAGE_MANIFEST.csv")

missing, extra, wrong = [], [], set()
listed = set()
for _, r in mf.iterrows():
    rel = str(r.path).strip()
    listed.add(rel)
    p = PKG / rel
    if not p.exists():
        missing.append(rel)

on_disk = {str(p.relative_to(PKG)) for p in PKG.rglob("*") if p.is_file()}
extra = sorted(on_disk - listed)
for rel in missing:
    print("MISSING:", rel)
for rel in extra:
    print("EXTRA  :", rel)
print(f"listed={len(listed)} on_disk={len(on_disk)} "
      f"missing={len(missing)} extra={len(extra)}")
sys.exit(1 if (missing or extra) else 0)
