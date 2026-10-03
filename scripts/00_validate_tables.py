#!/usr/bin/env python3
"""00_validate_tables.py — QC all CSV deliverables.

Checks every CSV in the previous feasibility package
(civilization_adaptation_feasibility/CIVILIZATION_ADAPTATION_FEASIBILITY/) and in
the new design-freeze package (CROP_RIGIDITY_DESIGN_FREEZE/ + analysis/):

  * readable as RFC4180 CSV (pandas read_csv, python csv)
  * consistent column count across all rows
  * UTF-8 decodable
  * no duplicated headers, no duplicated rows
  * no empty required fields (first column = row identifier)
  * missing-value representation unified to {NA, n/a, -, ''}

Writes analysis/00_qc_tables.csv and prints a summary.
"""
import csv
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PREV = ROOT.parent / "civilization_adaptation_feasibility" / "CIVILIZATION_ADAPTATION_FEASIBILITY"
HERE = ROOT / "CROP_RIGIDITY_DESIGN_FREEZE"
ANALYSIS = ROOT / "analysis"

ALLOWED_MISSING = {"", "NA", "n/a", "-"}


def scan_file(path: Path) -> dict:
    rec = {
        "file": str(path.relative_to(ROOT.parent)),
        "exists": True,
        "utf8": True,
        "rows": 0,
        "cols": 0,
        "col_counts": "",
        "malformed_lines": 0,
        "duplicated_headers": False,
        "duplicated_rows": 0,
        "empty_id_fields": 0,
        "missing_tokens": "",
        "pandas_ok": True,
        "issues": "",
    }
    try:
        raw = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        rec.update(utf8=False, pandas_ok=False, issues="not utf-8")
        return rec

    issues = []
    rows = []
    malformed = 0
    reader = csv.reader(raw.splitlines())
    for r in reader:
        if not r:
            malformed += 1
            continue
        rows.append(r)
    rec["malformed_lines"] = malformed
    if not rows:
        rec["issues"] = "empty file"
        return rec

    header = rows[0]
    rec["cols"] = len(header)
    rec["rows"] = len(rows) - 1
    counts = {len(r) for r in rows}
    rec["col_counts"] = "|".join(map(str, sorted(counts)))
    if len(counts) > 1:
        issues.append(f"inconsistent column counts {sorted(counts)}")
    if len(set(header)) != len(header):
        rec["duplicated_headers"] = True
        issues.append("duplicated header fields")
    seen = set()
    dup = 0
    empty_id = 0
    tokens = set()
    for r in rows[1:]:
        t = tuple(r)
        if t in seen:
            dup += 1
        seen.add(t)
        if r and r[0].strip() == "":
            empty_id += 1
        for cell in r:
            c = cell.strip()
            if c in ALLOWED_MISSING or c.lower() in {"nan", "null", "none"}:
                tokens.add(c if c else "<empty>")
    rec["duplicated_rows"] = dup
    rec["empty_id_fields"] = empty_id
    rec["missing_tokens"] = "|".join(sorted(tokens))
    bad_tokens = {t for t in tokens - {"<empty>"} if t not in ALLOWED_MISSING}
    if bad_tokens:
        issues.append(f"nonstandard missing tokens {sorted(bad_tokens)}")
    if dup:
        issues.append(f"{dup} duplicated rows")
    if empty_id:
        issues.append(f"{empty_id} rows with empty id field")
    if malformed:
        issues.append(f"{malformed} malformed lines")

    try:
        df = pd.read_csv(path)
        if df.shape[1] != len(header):
            issues.append("pandas column count mismatch")
    except Exception as e:  # noqa: BLE001
        rec["pandas_ok"] = False
        issues.append(f"pandas error: {e}")

    rec["issues"] = "; ".join(issues)
    return rec


def main() -> int:
    targets = (
        sorted(PREV.glob("*.csv"))
        + sorted(HERE.glob("*.csv"))
        + [p for p in sorted(ANALYSIS.glob("*.csv")) if p.name != "00_qc_tables.csv"]
    )
    recs = []
    for p in targets:
        if p.exists():
            recs.append(scan_file(p))
        else:
            recs.append({"file": str(p.relative_to(ROOT.parent)), "exists": False, "issues": "missing"})
    out = pd.DataFrame(recs)
    ANALYSIS.mkdir(exist_ok=True)
    out_path = ANALYSIS / "00_qc_tables.csv"
    out.to_csv(out_path, index=False)
    print(out[["file", "rows", "cols", "col_counts", "issues"]].to_string(index=False))
    n_bad = (out["issues"].fillna("") != "").sum()
    print(f"\n{n_bad} files with issues / {len(out)} scanned")
    return 0


if __name__ == "__main__":
    sys.exit(main())
