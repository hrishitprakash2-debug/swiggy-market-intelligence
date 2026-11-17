"""
06_recalc_excel.py — Force a real Excel recalculation and verify the results.

openpyxl writes formulas with no cached value, so a reviewer opening the file in
Google Sheets, a preview pane or LibreOffice sees blanks. This opens the workbook
in Excel invisibly, runs CalculateFullRebuild, saves, and then reads the cached
values back and compares them to figures computed independently in pandas.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
from openpyxl import load_workbook

ROOT = Path(__file__).resolve().parent.parent
XLSX = ROOT / "output" / "Swiggy_Market_Intelligence.xlsx"
CLEAN = ROOT / "data" / "clean"

# ---------------------------------------------------------------- recalculate
try:
    import win32com.client as win32
except ImportError:
    sys.exit("pywin32 not available — cannot recalculate")

excel = win32.DispatchEx("Excel.Application")
excel.Visible = False
excel.DisplayAlerts = False
try:
    wb = excel.Workbooks.Open(str(XLSX.resolve()))
    excel.CalculateFullRebuild()
    excel.CalculateUntilAsyncQueriesDone()
    wb.Save()
    wb.Close(SaveChanges=True)
    print("Excel recalculation: done, cached values written")
finally:
    excel.Quit()
    del excel

# ------------------------------------------------------------------- verify
nat = pd.read_csv(CLEAN / "restaurants_clean.csv")
sla = pd.read_csv(CLEAN / "metro_sla_clean.csv")
city_counts = nat.groupby("city_name").size()
cui_counts = nat.groupby("primary_cuisine").size()

expected = {
    "total_listings": len(nat),
    "cities_150plus": int((city_counts >= 150).sum()),
    "avg_cost": round(nat["cost_for_two"].mean(), 2),
    "avg_rating": round(nat["rating"].mean(), 3),
    "unrated_share": round(nat["rating"].isna().mean(), 4),
    "cuisines_400plus": int((cui_counts >= 400).sum()),
    "bangalore_listings": int(city_counts.get("Bangalore", 0)),
    "icecream_rating": round(nat.loc[nat.primary_cuisine == "Ice Cream", "rating"].mean(), 3),
    "northindian_share": round((nat.primary_cuisine == "North Indian").mean(), 4),
    "kolkata_breach45": round(
        (sla.loc[sla.city_name == "Kolkata", "delivery_min"] > 45).mean(), 4),
}

wb2 = load_workbook(XLSX, data_only=True)
dash = wb2["Dashboard"]
city = wb2["City Matrix"]
cui = wb2["Cuisine Matrix"]
sl = wb2["SLA Matrix"]

got = {
    "total_listings": dash["B6"].value,
    "cities_150plus": dash["D6"].value,
    "avg_cost": dash["F6"].value,
    "avg_rating": dash["H6"].value,
    "unrated_share": dash["J6"].value,
    "cuisines_400plus": dash["L6"].value,
    "bangalore_listings": city["B4"].value,
}
# cuisine + SLA lookups by label rather than fixed row
cui_rows = {cui.cell(row=r, column=1).value: r for r in range(4, 50)}
sla_rows = {sl.cell(row=r, column=1).value: r for r in range(4, 20)}
got["icecream_rating"] = cui.cell(row=cui_rows["Ice Cream"], column=5).value
got["northindian_share"] = cui.cell(row=cui_rows["North Indian"], column=3).value
got["kolkata_breach45"] = sl.cell(row=sla_rows["Kolkata"], column=4).value

print(f"\n{'metric':<22}{'Excel (recalced)':>20}{'pandas':>16}{'match':>8}")
print("-" * 66)
fails = []
for k, exp in expected.items():
    v = got.get(k)
    if v is None:
        ok = False
    elif isinstance(exp, int) and not isinstance(exp, bool):
        ok = int(round(float(v))) == exp
    else:
        ok = abs(float(v) - exp) <= max(0.002, abs(exp) * 0.01)
    if not ok:
        fails.append((k, v, exp))
    print(f"{k:<22}{str(round(v, 4) if isinstance(v, float) else v):>20}"
          f"{str(exp):>16}{'OK' if ok else 'MISMATCH':>8}")

print("\n" + ("ALL CHECKS PASS — workbook matches pandas" if not fails
              else f"{len(fails)} MISMATCHES: {fails}"))
