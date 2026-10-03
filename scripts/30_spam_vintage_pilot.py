#!/usr/bin/env python3
"""30_spam_vintage_pilot.py — SPAM2005 vs SPAM2010 harvested-area comparison.
Feasibility pilot: quantifies apparent pixel-level crop change across
SPAM vintages and how much survives spatial aggregation.
Extracts WHEA/MAIZ/RICE all-technology rasters from the persisted zips.
"""
import json
import zipfile
from pathlib import Path

import numpy as np
import rasterio

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "mapspam"
OUT = ROOT / "SUBNATIONAL_RIGIDITY_FEASIBILITY" / "analysis"
OUT.mkdir(parents=True, exist_ok=True)
TMP = Path("/tmp/spam_pilot"); TMP.mkdir(exist_ok=True)

CROPS = ["WHEA", "MAIZ", "RICE"]
Z05 = RAW / "spam2005v3r2_global_harv_area.geotiff.zip"
Z10 = RAW / "spam2010v2r0_global_harv_area.geotiff.zip"


def extract(zip_path, pattern, dest):
    with zipfile.ZipFile(zip_path) as z:
        for n in z.namelist():
            if n.endswith(".tif") and pattern in n:
                tgt = dest / Path(n).name
                tgt.write_bytes(z.read(n))
                return tgt
    raise FileNotFoundError(pattern)


def load(p):
    with rasterio.open(p) as r:
        a = r.read(1).astype(np.float64)
    a[a < 0] = 0
    return a


def block_l1(a05, a10, k):
    h, w = a05.shape
    b05 = a05[:h // k * k, :w // k * k].reshape(h // k, k, w // k, k).sum((1, 3))
    b10 = a10[:h // k * k, :w // k * k].reshape(h // k, k, w // k, k).sum((1, 3))
    m = (b05 > 0) | (b10 > 0)
    gone = ((b05 > 0) & (b10 == 0)).sum() / max((b05 > 0).sum(), 1)
    new = ((b05 == 0) & (b10 > 0)).sum() / max((b10 > 0).sum(), 1)
    return dict(L1=float(np.abs(b10[m] - b05[m]).sum()
                       / (b05[m].sum() + b10[m].sum())),
                corr=float(np.corrcoef(b05[m], b10[m])[0, 1]),
                gone=float(gone), new=float(new))


res = {}
for crop in CROPS:
    p05 = extract(Z05, f"_TA_{crop}_A", TMP)
    p10 = extract(Z10, f"_H_{crop}_A", TMP)
    a05, a10 = load(p05), load(p10)[:load(p05).shape[0]]
    res[crop] = dict(
        pixel=block_l1(a05, a10, 1),
        deg05=block_l1(a05, a10, 12),
        deg15=block_l1(a05, a10, 36),
        deg25=block_l1(a05, a10, 60),
        tot05_mha=float(a05.sum() / 1e6), tot10_mha=float(a10.sum() / 1e6),
        nat_d_mha=float(abs(a10.sum() - a05.sum()) / 1e6))

json.dump(res, open(OUT / "spam_vintage_pilot.json", "w"), indent=1)
print(json.dumps(res, indent=1))
