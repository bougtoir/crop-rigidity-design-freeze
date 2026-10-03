#!/usr/bin/env python3
"""03_build_ledger.py — regenerate DATA_SOURCE_LEDGER_v2.csv from data/raw."""
import hashlib
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
ACCESS = "2026-10-03"

META = [
    # glob, dataset, source, url, version, doi, license, method, coverage, missingness
    ("faostat_qcl_2026-02-25.feather", "FAOSTAT QCL (via OWID garden mirror)",
     "FAO / Our World in Data",
     "https://catalog.ourworldindata.org/garden/faostat/2026-02-25/faostat_qcl/faostat_qcl.feather",
     "OWID garden 2026-02-25 (FAOSTAT current)", "NA", "CC BY (OWID mirror); underlying FAO terms",
     "HTTPS GET (FAO bulk host unreachable from VM; OWID mirror used)",
     "254 countries x 169 items x 1961-2024; area harvested/yield/production",
     "reporting gaps concentrated in small states; filtered to >=10yr/windows"),
    ("mapspam/spam2005v3r2_global_harv_area.geotiff.zip", "MapSPAM 2005 v3.2 harvested area",
     "IFPRI / Harvard Dataverse",
     "https://dataverse.harvard.edu/api/access/datafile/3086558",
     "v3.2", "doi:10.7910/DVN/DHXBJX", "CC0/Dataverse terms",
     "Dataverse API file download (follow redirect)",
     "global 5-arcmin, 42 crops x irrigated/rainfed/etc", "model-allocated; no uncertainty fields in geotiff"),
    ("mapspam/spam2010v2r0_global_harv_area.geotiff.zip", "MapSPAM 2010 v2.0 harvested area",
     "IFPRI / Harvard Dataverse",
     "https://dataverse.harvard.edu/api/access/datafile/3985008",
     "v2.0", "doi:10.7910/DVN/PRFF8V", "CC0/Dataverse terms",
     "Dataverse API file download",
     "global 5-arcmin, 42 crops x production systems", "latest GLOBAL release; 2017 covers only SSA"),
    ("mapspam/ReadMe_2005.txt", "MapSPAM 2005 readme", "IFPRI/Dataverse",
     "https://dataverse.harvard.edu/api/access/datafile/3086282", "v3.2",
     "doi:10.7910/DVN/DHXBJX", "CC0", "Dataverse API", "documentation", "NA"),
    ("mapspam/ReadMe_2010.txt", "MapSPAM 2010 readme", "IFPRI/Dataverse",
     "https://dataverse.harvard.edu/api/access/datafile/3984174", "v2.0",
     "doi:10.7910/DVN/PRFF8V", "CC0", "Dataverse API", "documentation", "NA"),
    ("gaez/GAEZ-V4.RES05-SCI.TP-*.tif", "GAEZ v4 suitability index in classes",
     "FAO/IIASA via GCS fao-gismgr-gaez-v4-data",
     "https://storage.googleapis.com/fao-gismgr-gaez-v4-data/DATA/GAEZ-V4/MAPSET/RES05-SCI/",
     "GAEZ v4 (2021)", "NA", "GAEZ terms (non-commercial attribution)",
     "GCS bucket listing + GET", "5-arcmin global; WHE/COT/SUC; 1981-2010 CRUTS32 + 2041-2070 ENSEMBLE RCP8.5",
     "public mirror carries only 3 crops x 1 scenario x 2 periods"),
    ("gaez/GAEZ-V4.RES05-YLDL.TP-*.tif", "GAEZ v4 attainable yield",
     "FAO/IIASA via GCS",
     "https://storage.googleapis.com/fao-gismgr-gaez-v4-data/DATA/GAEZ-V4/MAPSET/RES05-YLDL/",
     "GAEZ v4 (2021)", "NA", "GAEZ terms", "GCS GET", "same coverage as RES05-SCI", "same limitation"),
    ("gaez/GAEZ-V4*.json", "GAEZ v4 metadata", "FAO/IIASA GCS",
     "https://storage.googleapis.com/fao-gismgr-gaez-v4-data/DATA/GAEZ-V4/", "v4", "NA",
     "GAEZ terms", "GCS GET", "mapset/dimension metadata", "NA"),
    ("mirca/*.zip", "MIRCA2000 (calendars, unit codes, cell areas, max cropped area)",
     "Uni Frankfurt / Zenodo", "https://zenodo.org/records/7422506", "MIRCA2000 (c.2000)",
     "doi:10.5281/zenodo.7422506", "CC BY", "Zenodo API",
     "5-arcmin global monthly cropping calendars, 26 crops", "baseline year ~2000 - temporal mismatch flagged"),
    ("isimip/lpjml_*yieldchange-mai*.nc", "ISIMIP3b LPJmL maize yield change",
     "ISIMIP / Jaegermeyr2021 derived outputs",
     "https://files.isimip.org/ISIMIP3b/DerivedOutputData/Jaegermeyr2021/LPJmL/",
     "ISIMIP3b", "doi:10.48364/ISIMIP.* (per dataset)", "CC BY 4.0",
     "ISIMIP API dataset lookup + files.isimip.org GET",
     "global 0.5deg, annual 2015-2099, SSP585; GCMs: GFDL-ESM4, IPSL-CM6A-LR",
     "yieldchange ratio, not absolute yield"),
    ("isimip/ggcmi-crop-calendar*.nc", "GGCMI phase3 crop calendar", "ISIMIP3a input",
     "https://files.isimip.org/ISIMIP3a/InputData/socioeconomic/crop_calendar/2015soc/",
     "2015soc", "NA", "CC BY 4.0", "files.isimip.org GET",
     "global 0.5deg crop calendar (barley, fully irrigated)", "NA"),
    ("spei/spei01.nc", "SPEIbase v2.11, 1-month", "CSIC", "https://spei.csic.es/spei_database_2_11/nc/spei01.nc",
     "2.11", "doi:10.20350/digitalCSIC/8508", "open", "HTTPS GET",
     "global 0.5deg monthly 1901-2023", "NA"),
    ("spei/spei12.nc", "SPEIbase v2.11, 12-month", "CSIC", "https://spei.csic.es/spei_database_2_11/nc/spei12.nc",
     "2.11", "doi:10.20350/digitalCSIC/8508", "open", "HTTPS GET",
     "global 0.5deg monthly 1901-2023", "NA"),
    ("-NASA POWER-", "NASA POWER agroclimatology API", "NASA",
     "https://power.larc.nasa.gov/api/", "current", "NA", "public domain",
     "reachability verified (200 JSON); per-query API, no bulk file persisted at freeze",
     "0.5deg daily/meteorological incl T2M, PRECTOTCORR", "NA"),
]


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


rows = []
for pattern, ds, src, url, ver, doi, lic, method, cov, miss in META:
    matches = sorted(RAW.glob(pattern))
    if pattern == "-NASA POWER-":
        matches = []
        rows.append(dict(dataset=ds, source=src, url=url, access_date_utc=ACCESS,
                         version=ver, doi=doi, license=lic,
                         archive_filename="(API)", size_bytes="NA", sha256="NA",
                         download_method=method, spatial_temporal_coverage=cov,
                         missingness=miss))
        continue
    for p in matches:
        rows.append(dict(dataset=ds, source=src, url=url, access_date_utc=ACCESS,
                         version=ver, doi=doi, license=lic,
                         archive_filename=str(p.relative_to(RAW)),
                         size_bytes=p.stat().st_size, sha256=sha256(p),
                         download_method=method, spatial_temporal_coverage=cov,
                         missingness=miss))

df = pd.DataFrame(rows)
out = ROOT / "CROP_RIGIDITY_DESIGN_FREEZE" / "DATA_SOURCE_LEDGER_v2.csv"
df.to_csv(out, index=False)
print(f"{len(df)} files -> {out}")
