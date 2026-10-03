#!/usr/bin/env python3
"""00_acquire_data.py — acquire the raw inputs added in the repair phase.
Idempotent: skips files that already exist. Hashes land in
DATA_SOURCE_LEDGER_v3.csv via 10_build_ledger_v3.py."""
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"

FILES = [
    ("mapspam/spam2000v3.0.7_global_harvested-area.geotiff.zip",
     "https://dataverse.harvard.edu/api/access/datafile/3666794"),
    ("mapspam/spam2000v3.0.7_global_harvested-area.dbf-csv.zip",
     "https://dataverse.harvard.edu/api/access/datafile/3666790"),
    ("mapspam/spam2000_ReadMe.txt",
     "https://dataverse.harvard.edu/api/access/datafile/3357441"),
    ("mapspam/spam2000_CropList.tab",
     "https://dataverse.harvard.edu/api/access/datafile/3357445"),
    ("isimip/countrymasks-fractional_5arcmin.nc",
     "https://files.isimip.org/ISIMIP3a/InputData/geo_conditions/"
     "countrymasks/countrymasks-fractional_5arcmin.nc"),
]

for rel, url in FILES:
    p = RAW / rel
    if p.exists():
        print("exists:", rel); continue
    p.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["curl", "-sL", "--retry", "3", "-o", str(p), url], check=True)
    print("fetched:", rel)

# NASA POWER monthly climate is fetched by 07_fetch_power_climate.py
# (per-country regional calls; resumable).
