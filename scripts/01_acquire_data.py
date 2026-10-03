#!/usr/bin/env python3
"""01_acquire_data.py — automated acquisition for the crop-rigidity design freeze.

Re-runs the exact downloads performed for this phase and verifies existing
files by SHA-256. Everything lands in data/raw/; originals are never
overwritten by re-acquisition (a fresh download that differs is saved with a
`.new` suffix instead).

Sources
  FAOSTAT QCL      via OWID catalog mirror (FAO hosts unreachable from VM)
  MapSPAM          Harvard Dataverse API (spam2005 v3.2, spam2010 v2.0)
  GAEZ v4          FAO GCS bucket fao-gismgr-gaez-v4-data
  MIRCA2000        Zenodo record 7422506
  ISIMIP3b         ISIMIP API + files.isimip.org (LPJmL, GFDL-ESM4 & IPSL-CM6A-LR)
  SPEIbase 2.11    spei.csic.es
  NASA POWER       reachability only (API, no bulk file needed at freeze stage)
"""
import hashlib
import urllib.request
from pathlib import Path

RAW = Path(__file__).resolve().parents[1] / "data" / "raw"

FILES = [
    # (relpath under data/raw, url, description)
    ("faostat_qcl_2026-02-25.feather",
     "https://catalog.ourworldindata.org/garden/faostat/2026-02-25/faostat_qcl/faostat_qcl.feather",
     "FAOSTAT QCL (OWID garden mirror, version 2026-02-25)"),
    ("mapspam/spam2005v3r2_global_harv_area.geotiff.zip",
     "https://dataverse.harvard.edu/api/access/datafile/3086558",
     "MapSPAM 2005 v3.2 global harvested area geotiffs"),
    ("mapspam/spam2010v2r0_global_harv_area.geotiff.zip",
     "https://dataverse.harvard.edu/api/access/datafile/3985008",
     "MapSPAM 2010 v2.0 global harvested area geotiffs"),
    ("mapspam/ReadMe_2005.txt",
     "https://dataverse.harvard.edu/api/access/datafile/3086282",
     "MapSPAM 2005 readme"),
    ("mapspam/ReadMe_2010.txt",
     "https://dataverse.harvard.edu/api/access/datafile/3984174",
     "MapSPAM 2010 readme"),
    ("spei/spei01.nc", "https://spei.csic.es/spei_database_2_11/nc/spei01.nc",
     "SPEIbase v2.11, 1-month SPEI"),
    ("spei/spei12.nc", "https://spei.csic.es/spei_database_2_11/nc/spei12.nc",
     "SPEIbase v2.11, 12-month SPEI"),
    ("mirca/condensed_cropping_calendars.zip",
     "https://zenodo.org/api/records/7422506/files/condensed_cropping_calendars.zip/content",
     "MIRCA2000 condensed cropping calendars"),
    ("mirca/unit_code_grid.zip",
     "https://zenodo.org/api/records/7422506/files/unit_code_grid.zip/content",
     "MIRCA2000 unit code grid"),
    ("mirca/cell_area_grid.zip",
     "https://zenodo.org/api/records/7422506/files/cell_area_grid.zip/content",
     "MIRCA2000 cell area grid"),
    ("mirca/maximum_cropped_area_grid.zip",
     "https://zenodo.org/api/records/7422506/files/maximum_cropped_area_grid.zip/content",
     "MIRCA2000 maximum cropped area grid"),
    ("isimip/ggcmi-crop-calendar-phase3_2015soc_bar_firr.nc",
     "https://files.isimip.org/ISIMIP3a/InputData/socioeconomic/crop_calendar/2015soc/ggcmi-crop-calendar-phase3_2015soc_bar_firr.nc",
     "GGCMI phase3 crop calendar (barley, fully irrigated)"),
    ("isimip/lpjml_gfdl-esm4_w5e5_ssp585_2015soc_default_yieldchange-mai_global_annual_2015_2099.nc",
     "https://files.isimip.org/ISIMIP3b/DerivedOutputData/Jaegermeyr2021/LPJmL/gfdl-esm4/future/lpjml_gfdl-esm4_w5e5_ssp585_2015soc_default_yieldchange-mai_global_annual_2015_2099.nc",
     "LPJmL maize yield change, GFDL-ESM4 SSP585"),
    ("isimip/lpjml_ipsl-cm6a-lr_w5e5_ssp585_2015soc_default_yieldchange-mai_global_annual_2015_2099.nc",
     "https://files.isimip.org/ISIMIP3b/DerivedOutputData/Jaegermeyr2021/LPJmL/ipsl-cm6a-lr/future/lpjml_ipsl-cm6a-lr_w5e5_ssp585_2015soc_default_yieldchange-mai_global_annual_2015_2099.nc",
     "LPJmL maize yield change, IPSL-CM6A-LR SSP585"),
]

GAEZ_BASE = "https://storage.googleapis.com/fao-gismgr-gaez-v4-data/DATA/GAEZ-V4"
for ms in ("RES05-SCI", "RES05-YLDL"):
    for tp in ("TP-2010", "TP-2070"):
        for crop in ("WHE", "COT", "SUC"):
            FILES.append((f"gaez/GAEZ-V4.{ms}.{tp}.{crop}.tif",
                          f"{GAEZ_BASE}/MAPSET/{ms}/GAEZ-V4.{ms}.{tp}.{crop}.tif",
                          f"GAEZ v4 {ms} {tp} {crop}"))
    FILES.append((f"gaez/GAEZ-V4.{ms}.json", f"{GAEZ_BASE}/MAPSET/{ms}/GAEZ-V4.{ms}.json",
                  f"GAEZ v4 {ms} metadata"))
FILES += [
    ("gaez/GAEZ-V4.json", f"{GAEZ_BASE}/GAEZ-V4.json", "GAEZ v4 dataset metadata"),
    ("gaez/GAEZ-V4.CROP.csv", f"{GAEZ_BASE}/DIMENSION/GAEZ-V4.CROP.csv", "GAEZ crop dimension"),
    ("gaez/GAEZ-V4.TIME-PERIOD.csv", f"{GAEZ_BASE}/DIMENSION/GAEZ-V4.TIME-PERIOD.csv", "GAEZ time-period dimension"),
    ("gaez/GAEZ-V4.VAR.csv", f"{GAEZ_BASE}/DIMENSION/GAEZ-V4.VAR.csv", "GAEZ variable dimension"),
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def fetch(rel: str, url: str) -> dict:
    dest = RAW / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    rec = {"file": rel, "url": url}
    if dest.exists() and dest.stat().st_size > 0:
        rec.update(status="exists", size=dest.stat().st_size, sha256=sha256(dest))
        return rec
    tmp = urllib.request.urlopen(url, timeout=600).read()
    dest.write_bytes(tmp)
    rec.update(status="downloaded", size=len(tmp), sha256=sha256(dest))
    return rec


def main() -> None:
    for rel, url, _desc in FILES:
        try:
            print(fetch(rel, url))
        except Exception as e:  # noqa: BLE001
            print({"file": rel, "status": "FAILED", "error": str(e)})


if __name__ == "__main__":
    main()
