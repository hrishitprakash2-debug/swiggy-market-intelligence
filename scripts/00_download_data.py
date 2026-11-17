"""
00_download_data.py — Fetch the two real Swiggy extracts.

Run before 01_clean.py when data/raw/ is empty. Verifies the row count on arrival so
a truncated download fails loudly instead of silently shrinking the analysis.
"""
from __future__ import annotations

import sys
import urllib.request
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
RAW.mkdir(parents=True, exist_ok=True)

HF = "https://huggingface.co/datasets"
SOURCES = [
    (f"{HF}/GowthamD03/Swiggy/resolve/main/swiggy.csv",
     "swiggy_national.csv", 148_541),
    (f"{HF}/jason1966/abhijitdahatonde_swiggy-restuarant-dataset/resolve/main/swiggy.csv",
     "swiggy_metro_sla.csv", 8_680),
]

for url, name, expected in SOURCES:
    dest = RAW / name
    if dest.exists():
        print(f"  {name}: already present ({dest.stat().st_size / 1e6:.1f} MB)")
    else:
        print(f"  {name}: downloading ...", flush=True)
        urllib.request.urlretrieve(url, dest)
        print(f"    -> {dest.stat().st_size / 1e6:.1f} MB")

    rows = len(pd.read_csv(dest, low_memory=False))
    ok = rows == expected
    print(f"    rows: {rows:,}  {'OK' if ok else f'MISMATCH (expected {expected:,})'}")
    if not ok:
        sys.exit(f"{name} row count mismatch — delete the file and retry")

print("\nraw data ready in data/raw/")
