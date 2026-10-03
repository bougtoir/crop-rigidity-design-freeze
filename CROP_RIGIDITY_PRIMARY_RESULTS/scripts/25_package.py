#!/usr/bin/env python3
"""25_package.py — PACKAGE_MANIFEST.csv + CROP_RIGIDITY_PRIMARY_RESULTS.zip"""
import hashlib
import shutil
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "CROP_RIGIDITY_PRIMARY_RESULTS"
SCRIPTS = ROOT / "scripts"
PKG_SCRIPTS = PKG / "scripts"
PKG_SCRIPTS.mkdir(exist_ok=True)
for s in sorted(SCRIPTS.glob("2*_*.py")):
    shutil.copy2(s, PKG_SCRIPTS / s.name)

rows = []
for p in sorted(PKG.rglob("*")):
    if p.is_file() and not p.name.startswith("_cache"):
        h = hashlib.sha256(p.read_bytes()).hexdigest()
        rows.append(dict(path=str(p.relative_to(PKG)),
                         size_bytes=p.stat().st_size, sha256=h))
pd.DataFrame(rows).to_csv(PKG / "PACKAGE_MANIFEST.csv", index=False)

zip_path = shutil.make_archive(str(ROOT / "CROP_RIGIDITY_PRIMARY_RESULTS"),
                               "zip", root_dir=ROOT,
                               base_dir="CROP_RIGIDITY_PRIMARY_RESULTS")
print(zip_path, Path(zip_path).stat().st_size)
