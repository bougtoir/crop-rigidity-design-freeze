#!/usr/bin/env python3
"""10_build_ledger_v3.py — DATA_SOURCE_LEDGER_v3.csv covering every raw file
under data/raw with URL/version/acquisition metadata."""
import hashlib
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PKG = ROOT / "CROP_RIGIDITY_PREANALYSIS_REPAIR"

META = {
    "faostat_qcl_2026-02-25.feather":
        ("OWID garden mirror of FAOSTAT QCL",
         "https://catalog.ourworldindata.org/garden/faostat/2026-02-25/faostat_qcl/faostat_qcl.feather",
         "2026-02-25"),
    "mapspam/spam2000v3.0.7_global_harvested-area.geotiff.zip":
        ("SPAM 2000 v3.0.7 harvested area geotiffs",
         "https://dataverse.harvard.edu/api/access/datafile/3666794",
         "v3.0.7 (avg 1999-2001)"),
    "mapspam/spam2000v3.0.7_global_harvested-area.dbf-csv.zip":
        ("SPAM 2000 v3.0.7 harvested area dbf-csv (per-pixel)",
         "https://dataverse.harvard.edu/api/access/datafile/3666790",
         "v3.0.7 (avg 1999-2001)"),
    "mapspam/spam2000_ReadMe.txt":
        ("SPAM2000 ReadMe", "https://dataverse.harvard.edu/api/access/datafile/3357441", "v3.0.7"),
    "mapspam/spam2000_CropList.tab":
        ("SPAM2000 crop list", "https://dataverse.harvard.edu/api/access/datafile/3357445", "v3.0.7"),
    "mapspam/spam2005v3r2_global_harv_area.geotiff.zip":
        ("SPAM 2005 harvested area (superseded for baseline; kept for reference)",
         "https://dataverse.harvard.edu/api/access/datafile/3154167", "v3r2"),
    "mapspam/spam2010v2r0_global_harv_area.geotiff.zip":
        ("SPAM 2010 harvested area (reference)",
         "https://dataverse.harvard.edu/api/access/datafile/3154170", "v2r0"),
    "mapspam/ReadMe_2005.txt": ("SPAM2005 ReadMe", "https://dataverse.harvard.edu/", "v3r2"),
    "mapspam/ReadMe_2010.txt": ("SPAM2010 ReadMe", "https://dataverse.harvard.edu/", "v2r0"),
    "isimip/countrymasks-fractional_5arcmin.nc":
        ("ISIMIP3a country masks 5 arcmin",
         "https://files.isimip.org/ISIMIP3a/InputData/geo_conditions/countrymasks/countrymasks-fractional_5arcmin.nc",
         "ISIMIP3a"),
    "mirca/MIRCA2000_cropped.zip":
        ("MIRCA2000 cropped areas (Zenodo 7422506)",
         "https://zenodo.org/record/7422506", "v2000"),
}
GAEZ = ("GAEZ v4 attainable yield/suitability rasters (public subset WHE/COT/SUC)",
        "https://storage.googleapis.com/fao-gismgr-gaez-v4-data/", "v4")
ISIMIP3B = ("ISIMIP3b LPJmL maize yield change (GFDL-ESM4/IPSL-CM6A-LR SSP585)",
            "https://files.isimip.org/", "ISIMIP3b")
POWER = ("NASA POWER monthly regional T2M/PRECTOTCORR 1984-2020",
         "https://power.larc.nasa.gov/api/temporal/monthly/regional",
         "accessed 2026-10-03")
SPEI = ("SPEIbase 2.11", "https://spei.csic.es/spei_database_2_11/", "2.11")

rows = []
now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
for p in sorted(RAW.rglob("*")):
    if not p.is_file():
        continue
    rel = str(p.relative_to(RAW))
    if rel.startswith("power/"):
        desc, url, ver = POWER
    elif rel.startswith("gaez/"):
        desc, url, ver = GAEZ
    elif rel.startswith("isimip/") and "countrymasks" not in rel:
        desc, url, ver = ISIMIP3B
    elif rel.startswith("spei/"):
        desc, url, ver = SPEI
    else:
        desc, url, ver = META.get(rel, (rel, "see v2 ledger", ""))
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 22), b""):
            h.update(chunk)
    rows.append(dict(file=rel, description=desc, source_url=url,
                     version=ver, retrieved_utc=now,
                     bytes=p.stat().st_size, sha256=h.hexdigest()))
pd.DataFrame(rows).to_csv(PKG / "DATA_SOURCE_LEDGER_v3.csv", index=False)
print(len(rows), "files ledgered")
