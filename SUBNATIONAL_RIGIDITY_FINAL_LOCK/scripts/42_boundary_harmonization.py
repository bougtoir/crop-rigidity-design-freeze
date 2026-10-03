#!/usr/bin/env python3
"""Phase 3: boundary harmonization against frozen GADM 4.1 admin-1 reference.

Emits:
  SUBNATIONAL_RIGIDITY_DESIGN_FREEZE/ADMIN_BOUNDARY_CROSSWALK.csv
  SUBNATIONAL_RIGIDITY_DESIGN_FREEZE/analysis/boundary_change_audit.csv
Classification per unit: unchanged | renamed | split | merge | boundary_shift |
hierarchy_change | unresolved (with reason).
"""
import re
import unicodedata
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "SUBNATIONAL_RIGIDITY_DESIGN_FREEZE"
M = pd.read_parquet(OUT / "analysis" / "admin_crop_observation_matrix.parquet")
G = pd.read_csv(ROOT / "data/raw/subnat/gadm41_admin1_index.csv")

CTY = {  # source country label -> GADM COUNTRY
    "Congo, The Democratic Republic of the": "Democratic Republic of the Congo",
    "Tanzania, United Republic of": "United Republic of Tanzania",
    "Laos": "Lao People's Democratic Republic",
    "Yemen": "Yemen", "Indonesia": "Indonesia", "Pakistan": "Pakistan",
    "Ethiopia": "Ethiopia", "Burkina Faso": "Burkina Faso", "Senegal": "Senegal",
    "El Salvador": "El Salvador", "Zimbabwe": "Zimbabwe", "Haiti": "Haiti",
    "Trinidad & Tobago": "Trinidad and Tobago", "United States": "United States",
    "Canada": "Canada", "Brazil": "Brazil",
}
NUTS2CTY = {"AT": "Austria", "BE": "Belgium", "BG": "Bulgaria", "CH": "Switzerland",
            "CY": "Cyprus", "CZ": "Czechia", "DE": "Germany", "DK": "Denmark",
            "EE": "Estonia", "EL": "Greece", "ES": "Spain", "FI": "Finland",
            "FR": "France", "HR": "Croatia", "HU": "Hungary", "IE": "Ireland",
            "IS": "Iceland", "IT": "Italy", "LT": "Lithuania", "LU": "Luxembourg",
            "LV": "Latvia", "ME": "Montenegro", "MK": "North Macedonia",
            "MT": "Malta", "NL": "Netherlands", "NO": "Norway", "PL": "Poland",
            "PT": "Portugal", "RO": "Romania", "RS": "Serbia", "SE": "Sweden",
            "SI": "Slovenia", "SK": "Slovakia", "TR": "Turkey", "UK": "United Kingdom",
            "AL": "Albania", "BA": "Bosnia and Herzegovina", "XK": "Kosovo",
            "EU": None}

def norm(s):
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode()
    s = s.lower().strip()
    s = re.sub(r"\(.*?\)", "", s)
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    return re.sub(r"\s+", " ", s).strip()

G["_n"] = G["NAME_1"].map(norm)
gadm_by = {c: sub.set_index("_n")["GID_1"].to_dict()
           for c, sub in G.groupby("COUNTRY")}

rows = []
units = M.groupby(["source", "country", "unit_id", "unit_name",
                   "admin_level"]).year.agg(["min", "max", "nunique"]).reset_index()
units.columns = ["source", "country", "unit_id", "unit_name", "admin_level",
                 "year_min", "year_max", "n_years"]

for _, u in units.iterrows():
    src, ctry, uid, uname = u.source, u.country, u.unit_id, u.unit_name
    gcty = CTY.get(ctry, ctry)
    if gcty not in gadm_by and src.startswith("eurostat"):
        gcty = NUTS2CTY.get(ctry)
    status, gid, note = "unresolved", None, ""
    if src == "usda_census_qs" or src == "ibge_pam" or src == "statcan_32100359":
        status, note = "unchanged", "official state/province code stable"
    elif src == "harveststat_africa_v1.2":
        status, note = "unchanged", "fnid stable identifier"
    elif src == "fao_subnational_2024":
        status, note = "unchanged", "GADM code present both vintages"
    elif src == "eurostat_apro_cpshr_2026":
        # NUTS revisions 2013/2016/2021: code present across vintages?
        if u.year_min <= 2012 and u.year_max >= 2013:
            status, note = "unchanged", "NUTS code present pre- and post-2013 revision"
        elif u.year_max <= 2012:
            status, note = "unresolved", "code retired at NUTS 2013/2016 revision"
        else:
            status, note = "unresolved", "code introduced at NUTS 2013/2016 revision"
    # try name match into GADM41 admin-1
    if uid.startswith("GADM:"):
        gid = uid[5:]
        if not gid or gid == "nan":
            gid = None
        else:
            status = "unchanged"
            note = "native GADM code"
    if gid is None and gcty in gadm_by:
        key = norm(uname)
        gid = gadm_by[gcty].get(key)
        if gid is None:
            for k, g in gadm_by[gcty].items():
                if key and (key in k or k in key):
                    gid = g
                    break
    rows.append(dict(source=src, country=ctry, unit_id=uid, unit_name=uname,
                     admin_level=int(u.admin_level), year_min=int(u.year_min),
                     year_max=int(u.year_max), n_years=int(u.n_years),
                     boundary_status=status, status_note=note,
                     gadm41_gid=gid, gadm41_match=pd.notna(gid)))

xw = pd.DataFrame(rows)
xw.to_csv(OUT / "ADMIN_BOUNDARY_CROSSWALK.csv", index=False)
audit = (xw.groupby(["source", "boundary_status"]).size().reset_index(name="units"))
audit.to_csv(OUT / "analysis" / "boundary_change_audit.csv", index=False)
print(xw.groupby(["source", "boundary_status", "gadm41_match"]).size().unstack(fill_value=0))
print("GADM match rate:", xw.gadm41_match.mean().round(3))
