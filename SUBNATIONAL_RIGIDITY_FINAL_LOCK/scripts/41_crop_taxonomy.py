#!/usr/bin/env python3
"""Phase 5: crop taxonomy crosswalk across sources -> canonical crop set.

Emits SUBNATIONAL_RIGIDITY_DESIGN_FREEZE/04_CROP_CROSSWALK.csv with one row per
(source, source_crop): canonical crop, FAOSTAT-style item, MIRCA class index,
lifecycle (annual / perennial_woody / perennial_nonwoody / forage / aggregate /
noncrop), and PRIMARY_CROP_SET membership.
"""
import re
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "SUBNATIONAL_RIGIDITY_DESIGN_FREEZE"
M = pd.read_parquet(OUT / "analysis" / "admin_crop_observation_matrix.parquet")

# canonical -> (faostat_item, mirca_class, lifecycle)
CANON = {
    "wheat": ("Wheat", 1, "annual"),
    "maize": ("Maize (corn)", 2, "annual"),
    "rice": ("Rice", 3, "annual"),
    "barley": ("Barley", 4, "annual"),
    "sorghum": ("Sorghum", 5, "annual"),
    "millet": ("Millet", 6, "annual"),
    "oats": ("Oats", 7, "annual"),
    "rye": ("Rye", 7, "annual"),
    "triticale": ("Triticale", 7, "annual"),
    "other_cereals": ("Cereals n.e.c.", 7, "annual"),
    "sugarcane": ("Sugar cane", 8, "perennial_nonwoody"),
    "sugar_beet": ("Sugar beet", 8, "annual"),
    "cassava": ("Cassava, fresh", 9, "annual"),
    "potato": ("Potatoes", 10, "annual"),
    "sweet_potato": ("Sweet potatoes", 10, "annual"),
    "yams": ("Yams", 10, "annual"),
    "other_roots": ("Roots and tubers n.e.c.", 10, "annual"),
    "soybean": ("Soya beans", 11, "annual"),
    "groundnut": ("Groundnuts, excluding shelled", 11, "annual"),
    "rapeseed": ("Rape or colza seed", 12, "annual"),
    "sunflower": ("Sunflower seed", 12, "annual"),
    "cotton": ("Seed cotton, unginned", 13, "annual"),
    "sesame": ("Sesame seed", 12, "annual"),
    "other_oilseeds": ("Oil crops n.e.c.", 12, "annual"),
    "dry_beans": ("Beans, dry", 15, "annual"),
    "chickpea": ("Chick peas, dry", 15, "annual"),
    "cowpea": ("Cow peas, dry", 15, "annual"),
    "pigeon_pea": ("Pigeon peas, dry", 15, "annual"),
    "lentil": ("Lentils, dry", 15, "annual"),
    "field_pea": ("Peas, dry", 15, "annual"),
    "other_pulses": ("Pulses n.e.c.", 15, "annual"),
    "coffee": ("Coffee, green", 17, "perennial_woody"),
    "tea": ("Tea leaves", 17, "perennial_woody"),
    "cocoa": ("Cocoa beans", 17, "perennial_woody"),
    "oil_palm": ("Oil palm fruit", 19, "perennial_woody"),
    "rubber": ("Rubber, natural", 19, "perennial_woody"),
    "coconut": ("Coconuts, in shell", 19, "perennial_woody"),
    "banana": ("Bananas", 20, "perennial_nonwoody"),
    "plantain": ("Plantains and others", 20, "perennial_nonwoody"),
    "pineapple": ("Pineapples", 20, "perennial_nonwoody"),
    "citrus": ("Citrus fruit n.e.c.", 21, "perennial_woody"),
    "grapes": ("Grapes", 22, "perennial_woody"),
    "apple": ("Apples", 21, "perennial_woody"),
    "mango": ("Mangoes, guavas and mangosteens", 21, "perennial_woody"),
    "dates": ("Dates", 21, "perennial_woody"),
    "cashew": ("Cashew nuts, in shell", 21, "perennial_woody"),
    "olive": ("Olives", 23, "perennial_woody"),
    "tobacco": ("Unmanufactured tobacco", 14, "annual"),
    "vegetables": ("Vegetables, fresh n.e.c.", 16, "annual"),
    "tomato": ("Tomatoes", 16, "annual"),
    "onion": ("Onions and shallots, dry", 16, "annual"),
    "forage": ("Forage products", 25, "forage"),
    "spices": ("Spices n.e.c.", 26, "annual"),
    "other_annual": ("Other crops n.e.c.", 26, "annual"),
    "other_perennial": ("Other permanent crops n.e.c.", 24, "perennial_woody"),
    "khat": ("Other stimulant crops", 26, "perennial_woody"),
    "sisal": ("Sisal, raw", 26, "perennial_woody"),
    "aggregate": (None, None, "aggregate"),
    "noncrop": (None, None, "noncrop"),
    "unmapped": (None, None, "unmapped"),
}
CANON_LC = set(CANON)

AGGREGATE_PAT = re.compile(
    r"(all\b|total|other\b|n\.e\.c|mixed|excluding|all dry|all, |, all$|"
    r"crops?$|lavouras|temporary|permanent crops$|grasses & legumes|"
    r"grasses totals|legumes totals|berry totals|vegetable totals|"
    r"cut christmas|grasses$|tame hay|haylage|mint$)", re.I)

# per-source mapping dicts (source_crop lower -> canonical)
PAT = [
    # wheat
    (r"wheat and spelt|common wheat|trigo|^wheat$|durum wheat$|wheat, durum|wheat, spring|wheat, winter|wheat, canada|wheat, other|winter wheat|spring wheat", "wheat"),
    (r"maize|corn for grain|milho|corn$|^corn ", "maize"),
    (r"^rice|rice, paddy|arroz|rice indica|rice japonica|paddy", "rice"),
    (r"barley|cevada", "barley"),
    (r"sorghum|sorgho|sorgo", "sorghum"),
    (r"millet$|millet,|bajra|finger millet|foxtail|pearl millet|proso", "millet"),
    (r"^oats|^oat\b|aveia", "oats"),
    (r"^rye\b|rye, |rye, all", "rye"),
    (r"triticale", "triticale"),
    (r"soghum|fonio|teff|buckwheat|canary seed|other cereals|spring cereal|winter cereal|maslin|mixed grains|cereal crops|quinoa|grain, n\.e\.c|cereals n", "other_cereals"),
    (r"sugarcane|sugar cane|cana", "sugarcane"),
    (r"sugar ?beet|r2000$", "sugar_beet"),
    (r"cassava|mandioca|manioc", "cassava"),
    (r"potato|potatoes|batata", "potato"),
    (r"sweet potato|sweet_potato", "sweet_potato"),
    (r"^yams?$|inhame", "yams"),
    (r"taro|cocoyam|root crops?|roots and tubers|sago|stachy roots", "other_roots"),
    (r"soybean|soya|soja", "soybean"),
    (r"groundnut|peanut|amendoim", "groundnut"),
    (r"rapeseed|canola|colza|turnip rape", "rapeseed"),
    (r"sunflower|girassol", "sunflower"),
    (r"cotton|algod", "cotton"),
    (r"sesame|gergelim", "sesame"),
    (r"linseed|flaxseed|mustard seed|safflower|niger seed|niger$|neug$|palm kernel|other oilseed|castor|mamona|oilseed|^rape$|jute", "other_oilseeds"),
    (r"bean|feij|gibto|goussi", "dry_beans"),
    (r"chick ?pea|chickpea|grão de bico", "chickpea"),
    (r"cowpea|cow pea|feijão-caupi|bambara", "cowpea"),
    (r"pigeon pea", "pigeon_pea"),
    (r"lentil", "lentil"),
    (r"field pea|peas, dry|grass pea|dry pea", "field_pea"),
    (r"pulse|dry pulses|vetch|lupins|protein crops|fava|mash$|peas$|^pea$|velvet", "other_pulses"),
    (r"coffee|café|cafe", "coffee"),
    (r"^tea\b|chá", "tea"),
    (r"cocoa|cacau", "cocoa"),
    (r"palm oil|oil palm|dendê|palm heart|palmito", "oil_palm"),
    (r"rubber|borracha", "rubber"),
    (r"coconut|coco", "coconut"),
    (r"banana", "banana"),
    (r"plantain", "plantain"),
    (r"pineapple|abacaxi|ananas", "pineapple"),
    (r"citrus|orange|laranja|lemon|lime|tangerine|mandarin|grapefruit", "citrus"),
    (r"grapes?$|vineyard|uva$", "grapes"),
    (r"apple|maçã|pear", "apple"),
    (r"mango|manga", "mango"),
    (r"dates?$|tâmara", "dates"),
    (r"cashew|caju", "cashew"),
    (r"olive|olives|azeitona", "olive"),
    (r"tobacco|fumo", "tobacco"),
    (r"tomato|tomate", "tomato"),
    (r"onion|cebola|shallot|garlic", "onion"),
    (r"vegetable|kale|cucumber|lettuce|pumpkin|pepper|chillies|chili|broccoli|melon|watermelon|melancia|okra|eggplant|cabbage|carrot|green bean|squash|pimenta|peas, green|sweet corn|spinach|cauliflower", "vegetables"),
    (r"hay\b|haylage|fodder|forage|silage|green maize|grassland|lucerne|alfalfa|clover|temporary grasses|plants harvested green|pasture|gramíneas", "forage"),
    (r"spice|clove|cardamom|coriander|caraway|borage|hemp$|vanilla|pimento|ginger|turmeric", "spices"),
    (r"khat|chat$|qhat", "khat"),
    (r"sisal|agave", "sisal"),
    (r"fruit|nuts|berries|avocado|papaya|guava|plum|peach|cherry|apricot|walnut|almond|hazelnut|pistachio|fig|pomegranate|strawberr|raspberr|blueberr|cranberr|chestnut|pecan|macadamia|permanent crops for human|enset|durian|pyrethrum|nutmeg|pam nut|sorrel", "other_perennial"),
]

EU_CODE = {
    "j0000": "forage", "g0000": "forage", "o1000": "olive", "w1000": "grapes",
    "t0000": "citrus", "r1000": "potato", "r2000": "sugar_beet",
    "r9000": "other_roots", "ara99": "other_annual", "h9000": "other_perennial",
    "pecr9": "other_perennial", "pecr": "aggregate", "c0000": "aggregate",
    "f0000": "other_perennial", "p0000": "aggregate", "r0000": "other_roots",
    "v0000_s0000": "vegetables", "i0000": "aggregate", "g1000": "forage",
    "e0000": "noncrop", "k0000": "noncrop", "l0000": "noncrop", "n0000": "noncrop",
    "q0000": "noncrop", "ara": "aggregate", "uaa": "noncrop",
}

DROP_PAT = re.compile(
    r"^uaa$|^ara$|arable land|utilised|fallow|^q0000$|^k0000$|^l0000$|^n0000$|"
    r"seed and seedling|flowers|ornamental|nurseries|kitchen gardens|"
    r"^i0000$|industrial crops$|fibre crops|fibre flax|hops|aromatic|energy crops|"
    r"cut christmas|christmas trees", re.I)

def classify(crop):
    c = crop.strip().lower()
    if c in EU_CODE:
        return EU_CODE[c]
    c = re.sub(r"\s*\(\d+\)\s*", "", c)          # strip (1)(2) footnotes
    c = re.sub(r"\s{2,}", " ", c).strip()
    if DROP_PAT.search(c):
        return "noncrop"
    if AGGREGATE_PAT.search(c):
        return "aggregate"
    for pat, can in PAT:
        if re.search(pat, c):
            return can
    return "unmapped"

rows = []
for (src, crop), g in M.groupby(["source", "crop"]):
    c0 = re.sub(r"\s*\(\d+\)\s*", "", str(crop).strip().lower())
    c0 = re.sub(r"\s{2,}", " ", c0)
    can = classify(str(crop))
    fa, mc, life = CANON[can]
    rows.append(dict(source=src, source_crop=crop, canonical_crop=can,
                     faostat_item=fa, mirca_class=mc, lifecycle=life,
                     total_area_ha=g["area_ha"].sum(),
                     in_primary_set=None))
xw = pd.DataFrame(rows)
PRIMARY = ["wheat", "rice", "maize", "barley", "sorghum", "millet", "cassava",
           "potato", "sweet_potato", "yams", "sugarcane", "soybean", "groundnut",
           "rapeseed", "sunflower", "cotton", "dry_beans", "cowpea", "coffee",
           "cocoa", "tea", "oil_palm", "banana", "other_cereals", "other_roots",
           "other_pulses", "other_oilseeds", "other_perennial"]
xw["in_primary_set"] = xw["canonical_crop"].isin(PRIMARY)
xw = xw.sort_values(["source", "total_area_ha"], ascending=[True, False])
xw.to_csv(OUT / "04_CROP_CROSSWALK.csv", index=False)
print(xw.groupby("canonical_crop").source_crop.count().sort_values(ascending=False).head(40))
print("unmapped share of area:",
      xw[xw.canonical_crop == "unmapped"].total_area_ha.sum() /
      xw.total_area_ha.sum())
print(xw[xw.canonical_crop == "unmapped"].sort_values("total_area_ha", ascending=False).head(30)[["source","source_crop","total_area_ha"]].to_string())
