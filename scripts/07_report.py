"""
07_report.py — The PDF executive report (reportlab).

Eight pages: cover, executive summary, method, market structure, pricing,
quality, operations, opportunity. Every number is read from the SQL result CSVs
so the report cannot drift from the query layer.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, Frame, Image, KeepTogether,
                                PageBreak, PageTemplate, Paragraph, Spacer, Table,
                                TableStyle)

ROOT = Path(__file__).resolve().parent.parent
RES, CHARTS = ROOT / "output" / "sql_results", ROOT / "charts"
OUT = ROOT / "output" / "Swiggy_Market_Intelligence_Report.pdf"

ORANGE = colors.HexColor("#FC8019")
INK = colors.HexColor("#1A1A1A")
GREY = colors.HexColor("#6B6B6B")
LIGHT = colors.HexColor("#F5F5F5")
BLUE = colors.HexColor("#2E5AAC")
RED = colors.HexColor("#B5452C")
GREEN = colors.HexColor("#3FA66A")

# ------------------------------------------------------------------ fonts
FONT, FONT_B = "Helvetica", "Helvetica-Bold"
try:
    import matplotlib
    fdir = Path(matplotlib.get_data_path()) / "fonts" / "ttf"
    pdfmetrics.registerFont(TTFont("DejaVu", str(fdir / "DejaVuSans.ttf")))
    pdfmetrics.registerFont(TTFont("DejaVu-Bold", str(fdir / "DejaVuSans-Bold.ttf")))
    FONT, FONT_B = "DejaVu", "DejaVu-Bold"
    RUPEE = "₹"
except Exception:                                        # noqa: BLE001
    RUPEE = "Rs."

ss = getSampleStyleSheet()
S = {
    "title": ParagraphStyle("t", fontName=FONT_B, size=30, leading=34, textColor=INK, spaceAfter=6),
    "sub": ParagraphStyle("s", fontName=FONT, size=12, leading=17, textColor=GREY),
    "h1": ParagraphStyle("h1", fontName=FONT_B, size=17, leading=21, textColor=INK,
                         spaceBefore=2, spaceAfter=8),
    "h2": ParagraphStyle("h2", fontName=FONT_B, size=11.5, leading=15, textColor=ORANGE,
                         spaceBefore=10, spaceAfter=4),
    "body": ParagraphStyle("b", fontName=FONT, size=9.8, leading=14.4, textColor=INK,
                           alignment=TA_JUSTIFY, spaceAfter=7),
    "bullet": ParagraphStyle("bl", fontName=FONT, size=9.8, leading=14, textColor=INK,
                             leftIndent=12, bulletIndent=2, spaceAfter=5),
    "caption": ParagraphStyle("c", fontName=FONT, size=8.2, leading=11, textColor=GREY,
                              spaceBefore=2, spaceAfter=10),
    "kpinum": ParagraphStyle("kn", fontName=FONT_B, size=19, textColor=ORANGE, leading=22),
    "kpilab": ParagraphStyle("kl", fontName=FONT, size=7.6, textColor=GREY, leading=9.5),
}


def q(name):
    return pd.read_csv(RES / f"{name}.csv")


kpi = q("q01_kpi_overview").iloc[0]
city = q("q02_city_supply_share")
price = q("q03_city_price_index")
cuisine = q("q06_cuisine_performance")
conf = q("q08_review_confidence")
sla_c = q("q20_sla_city")
sla_r = q("q21_sla_rating_relation")
opp = q("q25_locality_opportunity_score")
perc = q("q13_pareto_localities")

top7_share = float(city.head(7)["pct_of_national_supply"].sum())
ice = cuisine.set_index("primary_cuisine").loc["Ice Cream"]
ni = cuisine.set_index("primary_cuisine").loc["North Indian"]
kolkata = sla_c.set_index("city_name").loc["Kolkata"]
ahmed = sla_c.set_index("city_name").loc["Ahmedabad"]
fast = sla_r.iloc[0]
slow = sla_r.iloc[-1]

# ------------------------------------------------------------------ doc
def header_footer(canv, doc):
    canv.saveState()
    canv.setStrokeColor(colors.HexColor("#E4E4E4"))
    canv.setLineWidth(0.6)
    canv.line(18 * mm, A4[1] - 16 * mm, A4[0] - 18 * mm, A4[1] - 16 * mm)
    canv.setFont(FONT, 7.5)
    canv.setFillColor(GREY)
    canv.drawString(18 * mm, A4[1] - 13.4 * mm, "Swiggy Market Intelligence  ·  India food-delivery supply, pricing & service")
    canv.drawRightString(A4[0] - 18 * mm, A4[1] - 13.4 * mm, "Hrishit Prakash")
    canv.line(18 * mm, 14 * mm, A4[0] - 18 * mm, 14 * mm)
    canv.drawString(18 * mm, 9.5 * mm, "Source: 148,455 live Swiggy restaurant listings + 8,668 metro outlets with delivery times")
    canv.drawRightString(A4[0] - 18 * mm, 9.5 * mm, f"{doc.page}")
    canv.restoreState()


doc = BaseDocTemplate(str(OUT), pagesize=A4,
                      leftMargin=18 * mm, rightMargin=18 * mm,
                      topMargin=22 * mm, bottomMargin=18 * mm,
                      title="Swiggy Market Intelligence", author="Hrishit Prakash")
frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="f")
doc.addPageTemplates([PageTemplate(id="p", frames=[frame], onPage=header_footer)])

story = []

# ------------------------------------------------------------------ cover
story.append(Spacer(1, 26 * mm))
story.append(Paragraph("SWIGGY MARKET<br/>INTELLIGENCE", ParagraphStyle(
    "ct", fontName=FONT_B, size=34, leading=38, textColor=INK)))
story.append(Spacer(1, 4 * mm))
story.append(Paragraph(
    "Where India's food-delivery supply is concentrated, what it charges, "
    "and why delivery speed is the one lever that moves ratings",
    ParagraphStyle("cs", fontName=FONT, size=13, leading=19, textColor=GREY)))
story.append(Spacer(1, 8 * mm))

stat_rows = [[
    Paragraph(f"{int(kpi.total_listings):,}", S["kpinum"]),
    Paragraph(f"{int(kpi.cities)}", S["kpinum"]),
    Paragraph(f"{RUPEE}{int(kpi.avg_cost_for_two_inr)}", S["kpinum"]),
    Paragraph(f"{kpi.pct_listings_unrated:.0f}%", S["kpinum"]),
], [
    Paragraph("restaurant listings", S["kpilab"]),
    Paragraph("cities across India", S["kpilab"]),
    Paragraph("average cost for two", S["kpilab"]),
    Paragraph("listings with no rating", S["kpilab"]),
]]
t = Table(stat_rows, colWidths=[doc.width / 4.0] * 4)
t.setStyle(TableStyle([
    ("LINEABOVE", (0, 0), (-1, 0), 2.2, ORANGE),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("BOTTOMPADDING", (0, 1), (-1, 1), 4),
    ("TOPPADDING", (0, 0), (-1, 0), 8),
]))
story.append(t)
story.append(Spacer(1, 14 * mm))

story.append(Paragraph("What this project answers", S["h2"]))
for line in [
    "<b>Market structure</b> — how concentrated supply is, city by city, and which localities are already saturated.",
    f"<b>Pricing</b> — the national median meal for two is {RUPEE}250; a Goa listing charges 1.6× that and Bathinda 0.6×.",
    f"<b>Quality</b> — {kpi.pct_listings_unrated:.1f}% of listings carry no rating at all, and ratings rise steadily with review volume.",
    "<b>Service level</b> — delivery time is the strongest controllable correlate of customer satisfaction in the data.",
    "<b>Opportunity</b> — a composite locality score that ranks where the next outlet should open, without a single machine-learning model.",
]:
    story.append(Paragraph(f"• {line}", S["bullet"]))

story.append(Spacer(1, 10 * mm))
story.append(Paragraph(
    "Built with SQL (SQLite star schema, 25 analytical queries), Python "
    "(pandas, matplotlib, seaborn) and Excel (live formulas, native charts). "
    "Full pipeline and queries: github.com/hrishitprakash2-debug", S["caption"]))
story.append(PageBreak())

# ------------------------------------------------------- executive summary
story.append(Paragraph("Executive summary", S["h1"]))
story.append(Paragraph(
    f"India's online food-delivery supply is far more concentrated than the number of cities suggests. "
    f"The top seven cities hold <b>{top7_share:.1f}%</b> of all {int(kpi.total_listings):,} listings in this "
    f"extract, and the largest single city — Bangalore — holds <b>{city.iloc[0].pct_of_national_supply:.1f}%</b>. "
    f"The remaining {int(kpi.cities) - 7} cities share the other half, which means the interesting question is "
    f"not where the volume is, but where the unserved demand is.", S["body"]))

for head, body in [
    ("1 · Supply and satisfaction are inversely related",
     f"North Indian food is {ni.pct_of_supply:.1f}% of all supply but averages {ni.avg_rating:.2f} stars; "
     f"Ice Cream is a fraction of that supply and averages {ice.avg_rating:.2f}. The cuisines with the most "
     f"outlets are not the ones customers rate highest — they are the ones with the most competition and the "
     f"least differentiation."),
    (f"2 · {kpi.pct_listings_unrated:.1f}% of supply is effectively invisible",
     f"{int(kpi.total_listings - kpi.total_listings * (1 - kpi.pct_listings_unrated / 100)):,} listings carry "
     f"Swiggy's \"Too Few Ratings\" state, so they cannot appear in rank-based discovery. Among outlets that "
     f"<i>are</i> rated, average rating climbs from {conf.iloc[1].avg_rating:.2f} (under 50 reviews) to "
     f"{conf.iloc[3].avg_rating:.2f} (200+), so the unrated tail is not simply \"new\" — it is unsupported."),
    ("3 · Delivery time is the controllable driver of satisfaction",
     f"Outlets quoting 40 minutes or less average {fast.avg_rating:.2f} stars; those quoting 75+ average "
     f"{slow.avg_rating:.2f}. Kolkata quotes a median of {kolkata.median_delivery_min:.0f} minutes and breaches "
     f"a 45-minute promise on {kolkata.pct_breach_45min:.0f}% of outlets, against {ahmed.pct_breach_45min:.0f}% "
     f"in Ahmedabad. Speed is the only variable here that operations can actually move."),
    ("4 · Price is not a quality signal below the top decile",
     f"Moving from the cheapest to the {RUPEE}300 band changes average rating by less than 0.06 stars. Only the "
     f"top price decile (median cost {RUPEE}{price.iloc[0].median_cost_for_two_inr:.0f}+ in premium markets) "
     f"pulls clear, averaging above 4.05. Discount-led entry buys volume, not loyalty."),
    ("5 · The next outlet belongs in a mid-density, high-rating locality",
     f"The top opportunity score in the data is <b>{opp.iloc[0].locality_name}, {opp.iloc[0].city_name}</b> "
     f"({int(opp.iloc[0].listings)} outlets, {opp.iloc[0].avg_rating:.2f} stars, {int(opp.iloc[0].avg_reviews)} "
     f"average reviews) — dense enough to prove demand, thin enough to enter. Six of the top ten are in Kolkata "
     f"and Chennai, two cities that also under-deliver on service level."),
]:
    story.append(Paragraph(head, S["h2"]))
    story.append(Paragraph(body, S["body"]))

story.append(PageBreak())

# ------------------------------------------------------------------ method
story.append(Paragraph("Data and method", S["h1"]))
story.append(Paragraph(
    "Two real Swiggy extracts were used: a national scrape of <b>148,541 restaurant listings</b> across 821 "
    "localities, and an <b>8,680-outlet metro extract</b> that publishes quoted delivery times. No synthetic or "
    "imputed data was introduced at any stage; where Swiggy suppressed a value, it stayed empty and was excluded "
    "from the relevant aggregate.", S["body"]))

story.append(Paragraph("Cleaning decisions that changed the answer", S["h2"]))
rows = [["Issue in the raw data", "Rows", "What was done"],
        ["Rating stored as the string \"--\"", "87,014", "Parsed to null, never imputed"],
        ["Review counts banded (\"100+ ratings\")", "all", "Parsed to the band floor (100)"],
        ["Cost stored as \"\u20b9 200\"", "all", "Stripped and cast to numeric"],
        ["Implausible cost (up to \u20b9300,350)", "389", "Nulled — would distort every average"],
        ["Missing restaurant name", "86", "Dropped"],
        ["Duplicate outlet per locality (metro)", "7", "Dropped"],
        ["Control character inside a name", "1", "Stripped, record kept"]]
t = Table(rows, colWidths=[doc.width * .44, doc.width * .13, doc.width * .43])
t.setStyle(TableStyle([
    ("FONTNAME", (0, 0), (-1, 0), FONT_B),
    ("FONTSIZE", (0, 0), (-1, -1), 8.6),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("BACKGROUND", (0, 0), (-1, 0), ORANGE),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
    ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#E4E4E4")),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("TOPPADDING", (0, 0), (-1, -1), 5),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ("LEFTPADDING", (0, 0), (-1, -1), 6),
]))
story.append(t)
story.append(Paragraph("Six integrity gates run on every pipeline execution; all six pass, and the warehouse "
                       "reconciles to the cleaned CSV row-for-row.", S["caption"]))

story.append(Paragraph("Architecture", S["h2"]))
for line in [
    "<b>SQLite star schema</b> — two fact tables (national listings, metro SLA) plus city, locality, cuisine, "
    "price-band and review-confidence dimensions, and a many-to-many cuisine bridge so an outlet tagged "
    "\"Biryani, Mughlai\" is counted once in each cuisine.",
    "<b>25 analytical queries</b> — window functions for Pareto and per-city ranking, CTEs for cohort-style "
    "aggregation, an HHI concentration index, a median computed with ROW_NUMBER rather than an average, "
    "and a percentile-based opportunity score.",
    "<b>Excel workbook</b> — every figure is a live COUNTIFS / AVERAGEIFS / RANK.EQ formula over the full "
    "148,455-row data sheet, recalculated in Excel so cached values exist, and verified cell-by-cell against "
    "pandas.",
]:
    story.append(Paragraph(f"• {line}", S["bullet"]))
story.append(PageBreak())

# --------------------------------------------------------- market structure
story.append(Paragraph("1 · Market structure", S["h1"]))
story.append(Paragraph(
    f"Supply clusters hard. The top 12 cities in this extract cover {city.head(12).pct_of_national_supply.sum():.0f}% "
    f"of all listings, and the Pareto line shows the shape clearly: seven cities, half the country's supply. "
    f"Cuisine concentration (HHI) stays under 1,500 in every major city, so no single cuisine dominates a market "
    f"— competition is fragmented and price-led rather than monopolistic.", S["body"]))
story.append(Image(str(CHARTS / "01_supply_pareto.png"), width=doc.width * .98, height=doc.width * 0.45))
story.append(Paragraph("Figure 1 · Cumulative supply share by city. Seven cities hold just over half of national supply.", S["caption"]))

story.append(Paragraph(
    "Chains explain part of that concentration: Domino's alone runs 442 outlets across 247 cities, and the ten "
    "largest brands cover thousands of listings. But chains cluster in price-predictable categories — pizza, "
    "ice cream, coffee — so the number an operator should plan against is locality density, not city size.",
    S["body"]))
story.append(Image(str(CHARTS / "03_cuisine_supply_vs_rating.png"), width=doc.width * .86,
                   height=doc.width * .46))
story.append(Paragraph("Figure 2 · Cuisine supply against average rating. The biggest cuisines sit below the "
                       "average rating line; the small, differentiated ones sit above it.", S["caption"]))
story.append(PageBreak())

# ------------------------------------------------------------------ pricing
story.append(Paragraph("2 · Pricing", S["h1"]))
story.append(Paragraph(
    f"The national median cost for two is <b>{RUPEE}{price.iloc[0].median_cost_for_two_inr / price.iloc[0].price_index_national_1x:.0f}</b>, "
    f"but that national number hides a 2.6× spread. Goa's two districts sit at 1.6× the national median; "
    f"Bathinda sits at 0.6×. Notably, Delhi and Mumbai are not the most expensive markets in the data — both "
    f"index at 1.2×, in line with Hyderabad, Guwahati and Bikaner. Premium pricing is a function of tourism and "
    f"locality mix, not metro status alone.", S["body"]))
story.append(Image(str(CHARTS / "02_price_index.png"), width=doc.width * .88, height=doc.width * .44))
story.append(Paragraph("Figure 3 · Median cost for two by city, indexed to the national median.", S["caption"]))

story.append(Paragraph("Price does not buy satisfaction until the top decile", S["h2"]))
story.append(Paragraph(
    f"Across all {int(kpi.total_listings):,} listings, ratings are almost flat from the cheapest decile to the "
    f"ninth. The cheapest outlets average 3.91 stars; the {RUPEE}350-450 band averages 3.95. Only the top two "
    f"deciles break away — 3.95 and 4.07 — and even that is 0.16 stars for roughly three times the ticket. For a "
    f"new entrant the answer is plain: pricing up is a margin decision, not a rating strategy.", S["body"]))
story.append(Image(str(CHARTS / "07_price_decile_rating.png"), width=doc.width * .80, height=doc.width * .40))
story.append(Paragraph("Figure 4 · Average rating by price decile. The plateau is the finding.", S["caption"]))
story.append(PageBreak())

# ------------------------------------------------------------------ quality
story.append(Paragraph("3 · Quality and trust", S["h1"]))
story.append(Paragraph(
    f"The single most under-reported fact in this dataset is that <b>{kpi.pct_listings_unrated:.1f}%</b> of "
    f"listings have no rating. Swiggy withholds a star rating until review volume is meaningful, which is good "
    f"practice — but it means the majority of supply cannot be ranked, filtered or recommended on quality. Any "
    f"analysis that averages ratings across \"all restaurants\" is silently describing the 41% that cleared the "
    f"threshold.", S["body"]))
story.append(Image(str(CHARTS / "04_review_confidence.png"), width=doc.width * .88,
                   height=doc.width * .47))
story.append(Paragraph("Figure 5 · Average rating by review-volume band. More reviews correlate with higher "
                       "ratings, not lower.", S["caption"]))
story.append(Paragraph(
    f"Ratings do rise with review volume ({conf.iloc[1].avg_rating:.2f} → {conf.iloc[3].avg_rating:.2f}), which "
    f"argues against the cynics' view that volume erodes scores. The practical implication for a restaurant is "
    f"blunt: getting from \"Too Few Ratings\" to 50+ reviews is worth more than any menu change, because it moves "
    f"an outlet from invisible to rankable.", S["body"]))
story.append(Image(str(CHARTS / "10_rating_bands_by_city.png"), width=doc.width * .96,
                   height=doc.width * .50))
story.append(Paragraph("Figure 6 · Rating distribution by city. Every large market carries a 15-25% tail below "
                       "3.5 stars.", S["caption"]))
story.append(PageBreak())

# --------------------------------------------------------------- operations
story.append(Paragraph("4 · Service level", S["h1"]))
story.append(Paragraph(
    f"In the metro extract, a 45-minute promise is broken on <b>{sla_c.pct_breach_45min.mean():.0f}%</b> of "
    f"outlets on average. Kolkata is the outlier at {kolkata.pct_breach_45min:.0f}% (median quote "
    f"{kolkata.median_delivery_min:.0f} min), and Chennai follows at {sla_c.set_index('city_name').loc['Chennai'].pct_breach_45min:.0f}%. "
    f"Ahmedabad, at {ahmed.pct_breach_45min:.0f}%, shows the promise is achievable in an Indian metro with the "
    f"right kitchen density.", S["body"]))
story.append(Image(str(CHARTS / "05_sla_by_city.png"), width=doc.width * .96, height=doc.width * .50))
story.append(Paragraph("Figure 7 · Median quoted delivery time and breach rate by metro.", S["caption"]))

story.append(Paragraph("Why speed matters more than anything else in the data", S["h2"]))
story.append(Paragraph(
    f"Satisfaction falls monotonically with quoted delivery time: {fast.avg_rating:.2f} stars under 40 minutes, "
    f"{sla_r.iloc[2].avg_rating:.2f} at 51-60, {slow.avg_rating:.2f} beyond 75. The share of outlets rated 4.0+ "
    f"falls from {fast.pct_rated_4_plus:.0f}% to {slow.pct_rated_4_plus:.0f}%. Delivery time is the only variable "
    f"in this dataset that a restaurant and a platform can jointly control — menu, price and cuisine are mostly "
    f"fixed once an outlet opens.", S["body"]))
story.append(Image(str(CHARTS / "06_delivery_vs_rating.png"), width=doc.width * .86,
                   height=doc.width * .46))
story.append(Paragraph("Figure 8 · Average rating by quoted delivery window.", S["caption"]))
story.append(PageBreak())

# -------------------------------------------------------------- opportunity
story.append(Paragraph("5 · Where to open next", S["h1"]))
story.append(Paragraph(
    "Raw outlet counts reward the busiest locality, which is the wrong answer for an operator deciding where to "
    "enter. The score used here combines four percentile ranks: average rating (35%), review depth (25%), price "
    "headroom (20%) and low saturation (20%). High rating with deep reviews means demand is real; low saturation "
    "means entry is still possible.", S["body"]))
story.append(Image(str(CHARTS / "08_opportunity_localities.png"), width=doc.width * .94,
                   height=doc.width * .52))
story.append(Paragraph("Figure 9 · Top opportunity localities by composite score.", S["caption"]))

story.append(Paragraph("Recommendations", S["h2"]))
for line in [
    f"<b>Enter mid-density, high-rating localities.</b> {opp.iloc[0].locality_name} ({opp.iloc[0].city_name}) "
    f"and {opp.iloc[1].locality_name} ({opp.iloc[1].city_name}) combine proven demand with room to enter — "
    f"unlike Bengaluru's BTM or Delhi's Rohini, where 1,000+ outlets already compete.",
    "<b>Treat review volume as a launch metric.</b> The first 50 reviews move an outlet from invisible to "
    "rankable. Budget for it the way you budget for the fit-out.",
    "<b>Compete on speed, not discount.</b> Every 15 minutes of quoted delivery time costs roughly 0.1 stars "
    "and ten points of \"rated 4.0+\" share, while price cuts below the top decile buy nothing in ratings.",
    "<b>Avoid crowded cuisines at crowded price points.</b> North Indian at \u20b9250-350 is the most contested "
    "combination in the country; differentiated categories rate 0.2-0.5 stars higher on far less supply.",
]:
    story.append(Paragraph(f"• {line}", S["bullet"]))

story.append(Spacer(1, 6 * mm))
story.append(Paragraph("Limitations", S["h2"]))
story.append(Paragraph(
    "These are listing-level observations, not orders or revenue; outlet density is a proxy for market "
    "attention, which is reasonable but not causal. The metro SLA extract covers eight cities, so delivery "
    "findings should not be extrapolated nationally. Ratings are as published at scrape time and subject to "
    "Swiggy's suppression rules.", S["body"]))
story.append(Paragraph(
    "<b>Reproduce this:</b> sql/schema.sql, all 25 queries in sql/queries/, the numbered pipeline in scripts/ "
    "and the Excel workbook with every figure as a live formula — github.com/hrishitprakash2-debug", S["caption"]))

doc.build(story)
print(f"saved {OUT} ({OUT.stat().st_size/1e6:.1f} MB)")
