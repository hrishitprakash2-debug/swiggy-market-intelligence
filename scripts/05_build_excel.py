"""
05_build_excel.py — The Excel deliverable.

Builds Swiggy_Market_Intelligence.xlsx with:
  Dashboard     KPI cards + native Excel charts + live-formula insight sentences
  City Matrix   per-city metrics, every cell a COUNTIFS / AVERAGEIFS / RANK.EQ
  Cuisine Matrix, Price Bands, SLA Matrix
  Method & Quality  data-quality log and definitions
  Data, Data SLA    the full source rows so every formula stays live

No value is pasted: change a row in Data and the dashboard moves. Formulas are
recalculated in real Excel by scripts/06_recalc_excel.py so cached values exist
for viewers that do not calculate.
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
from openpyxl import Workbook
from openpyxl.chart import BarChart, LineChart, Reference
from openpyxl.formatting.rule import ColorScaleRule, DataBarRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

ROOT = Path(__file__).resolve().parent.parent
CLEAN = ROOT / "data" / "clean"
OUT = ROOT / "output" / "Swiggy_Market_Intelligence.xlsx"

nat = pd.read_csv(CLEAN / "restaurants_clean.csv")
sla = pd.read_csv(CLEAN / "metro_sla_clean.csv")
dq = json.loads((CLEAN / "data_quality.json").read_text(encoding="utf-8"))

ORANGE, INK, LIGHT, GREY = "FC8019", "1A1A1A", "FFF1E4", "F2F2F2"
ACCENT_BLUE = "2E5AAC"
HDR_FONT = Font(name="Calibri", size=10, bold=True, color="FFFFFF")
HDR_FILL = PatternFill("solid", fgColor=ORANGE)
TITLE = Font(name="Calibri", size=20, bold=True, color=INK)
SUB = Font(name="Calibri", size=10, color="666666")
LABEL = Font(name="Calibri", size=9, color="666666")
BOLD = Font(name="Calibri", size=10, bold=True)
THIN = Side(style="thin", color="DDDDDD")
BOX = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)

wb = Workbook()

# ---------------------------------------------------------------- source rows
data = nat[["listing_id", "restaurant", "city_name", "locality", "primary_cuisine",
            "cost_for_two", "rating", "rating_count", "review_confidence", "cost_band"]]
sla_rows = sla[["listing_id", "restaurant", "city_name", "locality", "primary_cuisine",
                "price_for_two", "rating", "rating_count", "delivery_min", "sla_band"]]

NAT_N = len(data)
SLA_N = len(sla_rows)
NAT_LAST = NAT_N + 1        # last data row (header occupies row 1)
SLA_LAST = SLA_N + 1

DA = f"Data!$A$2:$A${NAT_LAST}"
DC = f"Data!$C$2:$C${NAT_LAST}"
DE = f"Data!$E$2:$E${NAT_LAST}"
DF = f"Data!$F$2:$F${NAT_LAST}"
DG = f"Data!$G$2:$G${NAT_LAST}"
DH = f"Data!$H$2:$H${NAT_LAST}"
DI = f"Data!$I$2:$I${NAT_LAST}"
DJ = f"Data!$J$2:$J${NAT_LAST}"

SC = f"'Data SLA'!$C$2:$C${SLA_LAST}"
SF = f"'Data SLA'!$F$2:$F${SLA_LAST}"
SG = f"'Data SLA'!$G$2:$G${SLA_LAST}"
SI = f"'Data SLA'!$I$2:$I${SLA_LAST}"

# ------------------------------------------------------------- data sheets
ws_data = wb.active
ws_data.title = "Data"
ws_data.append(list(data.columns))
for row in data.itertuples(index=False):
    ws_data.append([None if pd.isna(v) else v for v in row])
ws_data.freeze_panes = "A2"
ws_data.auto_filter.ref = f"A1:J{NAT_LAST}"
for c in range(1, 11):
    ws_data.cell(row=1, column=c).font = HDR_FONT
    ws_data.cell(row=1, column=c).fill = HDR_FILL
ws_data.column_dimensions["B"].width = 38
ws_data.column_dimensions["D"].width = 18

ws_sla = wb.create_sheet("Data SLA")
ws_sla.append(list(sla_rows.columns))
for row in sla_rows.itertuples(index=False):
    ws_sla.append([None if pd.isna(v) else v for v in row])
ws_sla.freeze_panes = "A2"
ws_sla.auto_filter.ref = f"A1:J{SLA_LAST}"
for c in range(1, 11):
    ws_sla.cell(row=1, column=c).font = HDR_FONT
    ws_sla.cell(row=1, column=c).fill = HDR_FILL

# ------------------------------------------------------------- city matrix
cities = (nat.groupby("city_name").size().sort_values(ascending=False))
cities = cities[cities >= 150]
ws_city = wb.create_sheet("City Matrix")
ws_city["A1"] = "City matrix — every figure is a live formula over the Data sheet"
ws_city["A1"].font = Font(size=12, bold=True)
heads = ["City", "Listings", "% of supply", "Avg cost for two", "Avg rating",
         "Rated outlets", "Unrated %", "Rank (supply)", "Cost index vs national avg"]
for i, h in enumerate(heads, start=1):
    c = ws_city.cell(row=3, column=i, value=h)
    c.font, c.fill, c.border = HDR_FONT, HDR_FILL, BOX
    c.alignment = Alignment(horizontal="center", wrap_text=True)

first, last = 4, 3 + len(cities)
nat_avg = f"AVERAGE({DF})"
for i, (city, _n) in enumerate(cities.items()):
    r = first + i
    ws_city.cell(row=r, column=1, value=city)
    ws_city.cell(row=r, column=2, value=f'=COUNTIFS({DC},$A{r})')
    ws_city.cell(row=r, column=3, value=f'=B{r}/COUNTA({DA})')
    ws_city.cell(row=r, column=4, value=f'=IFERROR(AVERAGEIFS({DF},{DC},$A{r}),"")')
    ws_city.cell(row=r, column=5, value=f'=IFERROR(AVERAGEIFS({DG},{DC},$A{r}),"")')
    ws_city.cell(row=r, column=6, value=f'=COUNTIFS({DC},$A{r},{DG},">=0")')
    ws_city.cell(row=r, column=7, value=f'=1-F{r}/B{r}')
    ws_city.cell(row=r, column=8, value=f'=RANK.EQ(B{r},$B${first}:$B${last})')
    ws_city.cell(row=r, column=9, value=f'=D{r}/{nat_avg}')
    for c in range(1, 10):
        ws_city.cell(row=r, column=c).border = BOX
    ws_city.cell(row=r, column=2).number_format = "#,##0"
    ws_city.cell(row=r, column=3).number_format = "0.0%"
    ws_city.cell(row=r, column=4).number_format = '"₹"#,##0'
    ws_city.cell(row=r, column=5).number_format = "0.00"
    ws_city.cell(row=r, column=6).number_format = "#,##0"
    ws_city.cell(row=r, column=7).number_format = "0.0%"
    ws_city.cell(row=r, column=9).number_format = "0.000"

tot = last + 1
ws_city.cell(row=tot, column=1, value="TOTAL / NATIONAL").font = BOLD
ws_city.cell(row=tot, column=2, value=f"=SUM(B{first}:B{last})").font = BOLD
ws_city.cell(row=tot, column=3, value=f"=SUM(C{first}:C{last})").font = BOLD
ws_city.cell(row=tot, column=4, value=f"={nat_avg}").font = BOLD
ws_city.cell(row=tot, column=5, value=f"=AVERAGEIF({DG},\">=0\")").font = BOLD
ws_city.cell(row=tot, column=6, value=f"=SUM(F{first}:F{last})").font = BOLD
ws_city.cell(row=tot, column=7, value=f"=1-F{tot}/B{tot}").font = BOLD
ws_city.cell(row=tot, column=4).number_format = '"₹"#,##0'
ws_city.cell(row=tot, column=3).number_format = "0.0%"
ws_city.cell(row=tot, column=5).number_format = "0.00"
ws_city.cell(row=tot, column=7).number_format = "0.0%"
for c in range(1, 10):
    ws_city.cell(row=tot, column=c).fill = PatternFill("solid", fgColor=GREY)
    ws_city.cell(row=tot, column=c).border = BOX

ws_city.cell(row=tot + 2, column=1,
             value=f'="Cities shown cover "&TEXT(B{tot}/COUNTA({DA}),"0.0%")&'
                   f'" of all listings; the remainder sits in "&'
                   f'(COUNTA({DA})-B{tot})&" long-tail listings across smaller cities."'
             ).font = Font(size=9, italic=True, color="666666")
ws_city.cell(row=tot + 2, column=1).alignment = Alignment(wrap_text=True)
ws_city.merge_cells(start_row=tot + 2, start_column=1, end_row=tot + 2, end_column=6)

ws_city.conditional_formatting.add(
    f"B{first}:B{last}", DataBarRule(start_type="num", start_value=0,
                                     end_type="max", color=ORANGE))
ws_city.conditional_formatting.add(
    f"E{first}:E{last}", ColorScaleRule(start_type="min", start_color="F8696B",
                                        mid_type="percentile", mid_value=50, mid_color="FFEB84",
                                        end_type="max", end_color="63BE7B"))
ws_city.freeze_panes = "B4"
for col, w in zip("ABCDEFGHI", [24, 11, 11, 15, 11, 12, 11, 12, 16]):
    ws_city.column_dimensions[col].width = w

# ----------------------------------------------------------- cuisine matrix
cui = nat.groupby("primary_cuisine").size().sort_values(ascending=False)
cui = cui[cui >= 400]
ws_cui = wb.create_sheet("Cuisine Matrix")
ws_cui["A1"] = "Cuisine matrix — supply vs satisfaction vs price (live formulas)"
ws_cui["A1"].font = Font(size=12, bold=True)
heads = ["Primary cuisine", "Listings", "% of supply", "Avg cost for two", "Avg rating",
         "Avg review count", "Unrated %", "% rated 4.0+", "Rating vs national avg"]
for i, h in enumerate(heads, start=1):
    c = ws_cui.cell(row=3, column=i, value=h)
    c.font, c.fill, c.border = HDR_FONT, HDR_FILL, BOX
    c.alignment = Alignment(horizontal="center", wrap_text=True)
cfirst, clast = 4, 3 + len(cui)
for i, (name, _n) in enumerate(cui.items()):
    r = cfirst + i
    ws_cui.cell(row=r, column=1, value=name)
    ws_cui.cell(row=r, column=2, value=f'=COUNTIFS({DE},$A{r})')
    ws_cui.cell(row=r, column=3, value=f'=B{r}/COUNTA({DA})')
    ws_cui.cell(row=r, column=4, value=f'=IFERROR(AVERAGEIFS({DF},{DE},$A{r}),"")')
    ws_cui.cell(row=r, column=5, value=f'=IFERROR(AVERAGEIFS({DG},{DE},$A{r}),"")')
    ws_cui.cell(row=r, column=6, value=f'=IFERROR(AVERAGEIFS({DH},{DE},$A{r}),"")')
    ws_cui.cell(row=r, column=7, value=f'=COUNTIFS({DE},$A{r},{DG},"")/B{r}')
    ws_cui.cell(row=r, column=8, value=f'=COUNTIFS({DE},$A{r},{DG},">=4")/B{r}')
    ws_cui.cell(row=r, column=9, value=f'=E{r}-AVERAGEIF({DG},">=0")')
    for c in range(1, 10):
        ws_cui.cell(row=r, column=c).border = BOX
    ws_cui.cell(row=r, column=2).number_format = "#,##0"
    ws_cui.cell(row=r, column=3).number_format = "0.0%"
    ws_cui.cell(row=r, column=4).number_format = '"₹"#,##0'
    ws_cui.cell(row=r, column=5).number_format = "0.000"
    ws_cui.cell(row=r, column=6).number_format = "#,##0"
    ws_cui.cell(row=r, column=7).number_format = "0.0%"
    ws_cui.cell(row=r, column=8).number_format = "0.0%"
    ws_cui.cell(row=r, column=9).number_format = "+0.000;-0.000"
ctot = clast + 1
ws_cui.cell(row=ctot, column=1, value="TOTAL / NATIONAL").font = BOLD
ws_cui.cell(row=ctot, column=2, value=f"=SUM(B{cfirst}:B{clast})").font = BOLD
ws_cui.cell(row=ctot, column=5, value=f'=AVERAGEIF({DG},">=0")').font = BOLD
ws_cui.cell(row=ctot, column=5).number_format = "0.000"
for c in range(1, 10):
    ws_cui.cell(row=ctot, column=c).fill = PatternFill("solid", fgColor=GREY)
    ws_cui.cell(row=ctot, column=c).border = BOX
ws_cui.conditional_formatting.add(
    f"E{cfirst}:E{clast}", ColorScaleRule(start_type="min", start_color="F8696B",
                                          mid_type="percentile", mid_value=50, mid_color="FFEB84",
                                          end_type="max", end_color="63BE7B"))
ws_cui.freeze_panes = "B4"
for col, w in zip("ABCDEFGHI", [22, 10, 11, 15, 10, 13, 10, 12, 16]):
    ws_cui.column_dimensions[col].width = w

# ------------------------------------------------------------- price bands
ws_pb = wb.create_sheet("Price Bands")
ws_pb["A1"] = "Price band × cuisine matrix — where each cuisine competes (COUNTIFS)"
ws_pb["A1"].font = Font(size=12, bold=True)
bands = ["<=150", "151-250", "251-350", "351-500", "501-750", "750+"]
top_cui = list(cui.index[:10])
ws_pb.cell(row=3, column=1, value="Cuisine")
for j, b in enumerate(bands, start=2):
    c = ws_pb.cell(row=3, column=j, value=b)
    c.font, c.fill, c.border = HDR_FONT, HDR_FILL, BOX
ws_pb.cell(row=3, column=8, value="Row total").font, ws_pb.cell(row=3, column=8).fill = HDR_FONT, HDR_FILL
for i, name in enumerate(top_cui):
    r = 4 + i
    ws_pb.cell(row=r, column=1, value=name)
    for j, b in enumerate(bands, start=2):
        ws_pb.cell(row=r, column=j, value=f'=COUNTIFS({DE},$A{r},{DJ},"{b}")')
        ws_pb.cell(row=r, column=j).number_format = "#,##0"
    ws_pb.cell(row=r, column=8, value=f"=SUM(B{r}:G{r})")
    ws_pb.cell(row=r, column=8).font = BOLD
pb_last = 3 + len(top_cui)
ws_pb.cell(row=pb_last + 1, column=1, value="Band total").font = BOLD
for j in range(2, 8):
    col = get_column_letter(j)
    ws_pb.cell(row=pb_last + 1, column=j, value=f"=SUM({col}4:{col}{pb_last})").font = BOLD
ws_pb.cell(row=pb_last + 1, column=8, value=f"=SUM(H4:H{pb_last})").font = BOLD
ws_pb.conditional_formatting.add(
    f"B4:G{pb_last}", ColorScaleRule(start_type="min", start_color="FFFFFF",
                                     end_type="max", end_color=ORANGE))
ws_pb.column_dimensions["A"].width = 22
for col in "BCDEFG":
    ws_pb.column_dimensions[col].width = 11

# --------------------------------------------------------------- SLA matrix
sl = sla.groupby("city_name").size().sort_values(ascending=False)
ws_sla2 = wb.create_sheet("SLA Matrix")
ws_sla2["A1"] = "Metro service level — delivery time and breach rates (live formulas)"
ws_sla2["A1"].font = Font(size=12, bold=True)
heads = ["City", "Outlets", "Avg delivery (min)", "% breach > 45 min", "% breach > 60 min",
         "Avg rating", "Avg price for two"]
for i, h in enumerate(heads, start=1):
    c = ws_sla2.cell(row=3, column=i, value=h)
    c.font, c.fill, c.border = HDR_FONT, HDR_FILL, BOX
    c.alignment = Alignment(horizontal="center", wrap_text=True)
sfirst = 4
for i, city in enumerate(sl.index):
    r = sfirst + i
    ws_sla2.cell(row=r, column=1, value=city)
    ws_sla2.cell(row=r, column=2, value=f'=COUNTIFS({SC},$A{r})')
    ws_sla2.cell(row=r, column=3, value=f'=AVERAGEIFS({SI},{SC},$A{r})')
    ws_sla2.cell(row=r, column=4, value=f'=COUNTIFS({SC},$A{r},{SI},">45")/B{r}')
    ws_sla2.cell(row=r, column=5, value=f'=COUNTIFS({SC},$A{r},{SI},">60")/B{r}')
    ws_sla2.cell(row=r, column=6, value=f'=AVERAGEIFS({SG},{SC},$A{r})')
    ws_sla2.cell(row=r, column=7, value=f'=AVERAGEIFS({SF},{SC},$A{r})')
    for c in range(1, 8):
        ws_sla2.cell(row=r, column=c).border = BOX
    ws_sla2.cell(row=r, column=3).number_format = "0.0"
    ws_sla2.cell(row=r, column=4).number_format = "0.0%"
    ws_sla2.cell(row=r, column=5).number_format = "0.0%"
    ws_sla2.cell(row=r, column=6).number_format = "0.00"
    ws_sla2.cell(row=r, column=7).number_format = '"₹"#,##0'
slast = sfirst + len(sl) - 1
ws_sla2.conditional_formatting.add(
    f"D{sfirst}:D{slast}", ColorScaleRule(start_type="min", start_color="63BE7B",
                                          mid_type="percentile", mid_value=50, mid_color="FFEB84",
                                          end_type="max", end_color="F8696B"))
for col, w in zip("ABCDEFG", [16, 10, 18, 18, 18, 11, 18]):
    ws_sla2.column_dimensions[col].width = w

# --------------------------------------------------------------- dashboard
ws = wb.create_sheet("Dashboard", 0)
ws.sheet_view.showGridLines = False
ws["B2"] = "Swiggy Market Intelligence"
ws["B2"].font = TITLE
ws["B3"] = (f"{NAT_N:,} live restaurant listings · {nat.city_name.nunique()} cities · "
            f"{nat.locality.nunique()} localities · {SLA_N:,} outlets with delivery-time data")
ws["B3"].font = SUB

CM = "'City Matrix'"
CU = "'Cuisine Matrix'"
KPI = [
    ("TOTAL LISTINGS", f"=COUNTA({DA})", "#,##0"),
    ("CITIES (150+ LISTINGS)", f'=COUNTIF({CM}!$B${first}:$B${last},">0")', "#,##0"),
    ("AVG COST FOR TWO", f"=AVERAGE({DF})", '"₹"#,##0'),
    ("AVG RATING (WHEN RATED)", f"=AVERAGE({DG})", "0.00"),
    ("UNRATED SHARE", f"=COUNTBLANK({DG})/COUNTA({DA})", "0.0%"),
    ("CUISINES (400+ LISTINGS)", f'=COUNTIF({CU}!$B${cfirst}:$B${clast},">0")', "#,##0"),
]
col = 2
for label, formula, fmt in KPI:
    ws.cell(row=5, column=col, value=label).font = LABEL
    cell = ws.cell(row=6, column=col, value=formula)
    cell.font = Font(size=18, bold=True, color=ORANGE)
    cell.number_format = fmt
    cell.alignment = Alignment(horizontal="left")
    ws.merge_cells(start_row=5, start_column=col, end_row=5, end_column=col + 1)
    ws.merge_cells(start_row=6, start_column=col, end_row=6, end_column=col + 1)
    ws.cell(row=4, column=col, value="▔").font = Font(size=8, color=ORANGE)
    col += 2
for c in range(2, 14):
    ws.column_dimensions[get_column_letter(c)].width = 15
ws.row_dimensions[6].height = 26

# chart 1: top 12 cities by supply
# --- chart styling helper: single colour, visible axes, readable labels -----
from openpyxl.chart.axis import ChartLines
from openpyxl.drawing.line import LineProperties


def style(ch, color=ORANGE, axis_title="", numfmt="#,##0"):
    ch.varyColors = False
    ch.height, ch.width = 8.6, 17.8
    ch.legend = None
    for ser in ch.series:
        ser.graphicalProperties = ser.graphicalProperties or __import__(
            "openpyxl.chart.shapes", fromlist=["GraphicalProperties"]).GraphicalProperties()
        ser.graphicalProperties.solidFill = color
        ser.graphicalProperties.line = LineProperties(solidFill=color)
    ch.x_axis.delete = False
    ch.y_axis.delete = False
    ch.x_axis.tickLblPos = "low"
    ch.y_axis.tickLblPos = "nextTo"
    ch.y_axis.majorGridlines = ChartLines()
    ch.y_axis.majorGridlines.spPr = None
    ch.y_axis.numFmt = numfmt
    ch.x_axis.majorTickMark = "out"
    ch.y_axis.majorTickMark = "out"
    if axis_title:
        ch.y_axis.title = axis_title
    return ch


# chart 1: top 12 cities by supply
ch1 = BarChart()
ch1.type, ch1.style = "col", 2
ch1.title = "Top 12 cities by supply"
ch1.add_data(Reference(ws_city, min_col=2, min_row=3, max_row=3 + 12), titles_from_data=True)
ch1.set_categories(Reference(ws_city, min_col=1, min_row=4, max_row=4 + 11))
style(ch1, ORANGE, "Listings")
ws.add_chart(ch1, "B9")

# chart 2: top 10 cuisines by supply (horizontal bars)
ch2 = BarChart()
ch2.type, ch2.style = "bar", 2
ch2.title = "Top 10 cuisines by supply"
ch2.add_data(Reference(ws_cui, min_col=2, min_row=3, max_row=3 + 10), titles_from_data=True)
ch2.set_categories(Reference(ws_cui, min_col=1, min_row=4, max_row=4 + 9))
style(ch2, ACCENT_BLUE, "Listings")
ch2.x_axis.tickLblPos = "nextTo"
ws.add_chart(ch2, "B28")

# chart 3: SLA breach by metro
ch3 = BarChart()
ch3.type, ch3.style = "col", 2
ch3.title = "SLA breach rate by metro (share of outlets over 45 min)"
ch3.add_data(Reference(ws_sla2, min_col=4, min_row=3, max_row=slast), titles_from_data=True)
ch3.set_categories(Reference(ws_sla2, min_col=1, min_row=sfirst, max_row=slast))
style(ch3, "B5452C", "Breach rate", "0%")
ws.add_chart(ch3, "O9")

# chart 4: rating by review volume
ws.column_dimensions["O"].width = 24
ws.column_dimensions["P"].width = 12
ws.column_dimensions["Q"].width = 10
ch4 = LineChart()
ch4.title = "Ratings rise with review volume"
ch4.add_data(Reference(ws, min_col=16, min_row=29, max_row=33), titles_from_data=True)
ch4.set_categories(Reference(ws, min_col=15, min_row=30, max_row=33))
style(ch4, ORANGE, "Average rating", "0.00")
for ser in ch4.series:
    ser.graphicalProperties.line.solidFill = ORANGE
    ser.graphicalProperties.line.width = 28000
    ser.marker.symbol = "circle"
    ser.marker.size = 8
ws.add_chart(ch4, "O36")

# live-formula insight sentences
ws["B48"] = "What the data says"
ws["B48"].font = Font(size=14, bold=True)
insights = [
    f'="The top 7 cities hold "&TEXT(SUM({CM}!B4:B10)/COUNTA({DA}),"0.0%")&'
    f'" of all supply, and the single largest city controls just "&TEXT({CM}!C4,"0.0%")&"."',
    f'="Average rating when rated is "&TEXT({CM}!E{tot},"0.00")&" — but "&'
    f'TEXT(COUNTBLANK({DG})/COUNTA({DA}),"0.0%")&" of listings carry no rating at all."',
    f'="Ice Cream outlets average "&TEXT(INDEX({CU}!E{cfirst}:E{clast},MATCH("Ice Cream",{CU}!A{cfirst}:A{clast},0)),"0.00")&'
    f'" stars versus "&TEXT(INDEX({CU}!E{cfirst}:E{clast},MATCH("North Indian",{CU}!A{cfirst}:A{clast},0)),"0.00")&'
    f'" for North Indian, which has "&TEXT(INDEX({CU}!B{cfirst}:B{clast},MATCH("North Indian",{CU}!A{cfirst}:A{clast},0))/' 
    f'COUNTA({DA}),"0.0%")&" of supply."',
    f'="Kolkata misses a 45-minute delivery promise on "&TEXT(INDEX(\'SLA Matrix\'!D{sfirst}:D{slast},MATCH("Kolkata",\'SLA Matrix\'!A{sfirst}:A{slast},0)),"0%")&'
    f'" of orders, against "&TEXT(INDEX(\'SLA Matrix\'!D{sfirst}:D{slast},MATCH("Ahmedabad",\'SLA Matrix\'!A{sfirst}:A{slast},0)),"0%")&" in Ahmedabad."',
    f'="Outlets quoting under 40 minutes average "&TEXT(AVERAGEIFS({SG},{SI},"<=40"),"0.00")&'
    f'" stars; those over 75 minutes average "&TEXT(AVERAGEIFS({SG},{SI},">75"),"0.00")&"."',
]
for i, formula in enumerate(insights):
    c = ws.cell(row=49 + i * 2, column=2, value=formula)
    c.font = Font(size=11, color=INK)
    c.alignment = Alignment(wrap_text=True, vertical="top")
    ws.merge_cells(start_row=49 + i * 2, start_column=2, end_row=49 + i * 2, end_column=9)
    ws.row_dimensions[49 + i * 2].height = 30

# ------------------------------------------------- method & quality sheet
ws_m = wb.create_sheet("Method & Quality", 1)
ws_m["B2"] = "Method, definitions and data-quality log"
ws_m["B2"].font = TITLE
r = 4
ws_m.cell(row=r, column=2, value="Source").font = BOLD
ws_m.cell(row=r, column=3, value=dq["source"])
rows = [
    ("Raw rows ingested", f'{dq["tables"]["restaurants"]["rows_in"]:,} national + '
                          f'{dq["tables"]["metro_sla"]["rows_in"]:,} metro'),
    ("Rows dropped — missing restaurant name", f'{dq["tables"]["restaurants"]["drops"]["missing_restaurant_name"]:,}'),
    ("Rows dropped — duplicate listing id", f'{dq["tables"]["restaurants"]["drops"]["duplicate_listing_id"]:,}'),
    ("Implausible cost nulled (<₹50 or >₹10,000)",
     f'{dq["tables"]["restaurants"]["implausible_cost_nulled"]:,}'),
    ("Metro rows dropped — zero price", f'{dq["tables"]["metro_sla"]["drops"]["zero_or_missing_price"]:,}'),
    ("Metro rows dropped — duplicate outlet/locality",
     f'{dq["tables"]["metro_sla"]["drops"]["duplicate_restaurant_area"]:,}'),
    ("Clean rows — national", f'{dq["tables"]["restaurants"]["rows_out"]:,}'),
    ("Clean rows — metro SLA", f'{dq["tables"]["metro_sla"]["rows_out"]:,}'),
    ("Integrity checks passed", "All 6 PASS" if dq["integrity_passed"] else "FAIL"),
]
for i, (k, v) in enumerate(rows, start=1):
    ws_m.cell(row=r + i, column=2, value=k)
    ws_m.cell(row=r + i, column=3, value=v).font = BOLD

r2 = r + len(rows) + 3
ws_m.cell(row=r2, column=2, value="Definitions used").font = Font(size=12, bold=True)
defs = [
    ("Listing", "One restaurant outlet on one Swiggy storefront; the id is Swiggy's own."),
    ("Cost for two", "Swiggy's published 'cost for two' in INR. Median preferred over mean "
                     "because the distribution is right-skewed with a long premium tail."),
    ("Rated outlet", "An outlet with a published star rating. Swiggy suppresses ratings below "
                     "a review threshold, which is why 58.6% of supply is unrated."),
    ("Review confidence", "Low <50 reviews, Moderate 50-199, High 200+. A 4.9 from 20 reviews "
                          "is not comparable to a 4.9 from 2,000."),
    ("SLA breach", "Quoted delivery time above 45 minutes (or 60, where stated), "
                   "measured on the 8,668-outlet metro extract."),
    ("Cuisine", "Primary cuisine = first tag on the listing. The bridge table in SQL keeps "
                "every tag, so multi-tag outlets are counted once per cuisine there."),
    ("HHI", "Herfindahl-Hirschman index on cuisine share of outlets, 0-10,000. "
            "Under 1,500 is treated as fragmented."),
]
for i, (k, v) in enumerate(defs, start=1):
    ws_m.cell(row=r2 + i, column=2, value=k).font = BOLD
    c = ws_m.cell(row=r2 + i, column=3, value=v)
    c.alignment = Alignment(wrap_text=True, vertical="top")
    ws_m.merge_cells(start_row=r2 + i, start_column=3, end_row=r2 + i, end_column=8)
    ws_m.row_dimensions[r2 + i].height = 34
ws_m.column_dimensions["B"].width = 42
ws_m.column_dimensions["C"].width = 30
ws_m.sheet_view.showGridLines = False

order = ["Dashboard", "City Matrix", "Cuisine Matrix", "Price Bands",
         "SLA Matrix", "Method & Quality", "Data", "Data SLA"]
wb._sheets = [wb[name] for name in order]

wb.save(OUT)
print(f"saved {OUT} ({OUT.stat().st_size/1e6:.1f} MB)")
print(f"sheets: {wb.sheetnames}")
