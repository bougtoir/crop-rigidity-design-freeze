#!/usr/bin/env python3
"""12_build_ledger_v4.py — DATA_SOURCE_LEDGER_v4.csv for the final lock.

Raw inputs are identical to the repair phase (v3 ledger) plus the
extracted MIRCA unit_code.asc lookup grid (derived from
unit_code_grid.zip, which is itself ledgered). Rows: file, description,
source_url, version, retrieved_utc, bytes, sha256.
"""
import hashlib
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PKG = ROOT / "CROP_RIGIDITY_FINAL_LOCK"
PKG.mkdir(exist_ok=True)

v3 = pd.read_csv(ROOT / "CROP_RIGIDITY_PREANALYSIS_REPAIR" /
                 "DATA_SOURCE_LEDGER_v3.csv")
rows = [v3]

extra = []
for rel, desc in [
    ("mirca/unit_code_grid/unit_code.asc",
     "extracted MIRCA2000 5-arcmin calendar-unit grid (from unit_code_grid.zip)"),
]:
    p = RAW / rel
    if p.exists():
        extra.append(dict(
            file=rel, description=desc, source_url="derived: unit_code_grid.zip",
            version="MIRCA2000 v1.1", retrieved_utc="2026-10-03T11:30:00Z",
            bytes=p.stat().st_size,
            sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
rows.append(pd.DataFrame(extra))
led = pd.concat(rows, ignore_index=True)
led.to_csv(PKG / "DATA_SOURCE_LEDGER_v4.csv", index=False)
print("ledger v4:", len(led), "rows")
