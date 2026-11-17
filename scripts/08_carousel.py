"""
08_carousel.py — The LinkedIn carousel as an 8-slide PDF (1600x900).

LinkedIn renders a PDF post as a swipeable document, which is why the slides are
laid out here rather than exported as loose PNGs. Headline, chart, one line of
proof: the three things a scroll-pausing slide needs.
"""
from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer

ROOT = Path(__file__).resolve().parent.parent
CHARTS = ROOT / "charts"
OUT = ROOT / "output" / "Swiggy_Carousel.pdf"

W, H = 1600, 900
ORANGE = colors.HexColor("#FC8019")
INK = colors.HexColor("#111111")
GREY = colors.HexColor("#6B6B6B")

F, FB = "Helvetica", "Helvetica-Bold"
try:
    import matplotlib
    fd = Path(matplotlib.get_data_path()) / "fonts" / "ttf"
    pdfmetrics.registerFont(TTFont("DJ", str(fd / "DejaVuSans.ttf")))
    pdfmetrics.registerFont(TTFont("DJ-B", str(fd / "DejaVuSans-Bold.ttf")))
    F, FB = "DJ", "DJ-B"
except Exception:                                     # noqa: BLE001
    pass

HEAD = ParagraphStyle("h", fontName=FB, size=54, leading=60, textColor=INK)
HEAD_S = ParagraphStyle("hs", fontName=FB, size=46, leading=52, textColor=INK)
LEAD = ParagraphStyle("l", fontName=F, size=24, leading=33, textColor=GREY)
PROOF = ParagraphStyle("p", fontName=FB, size=27, leading=36, textColor=ORANGE)
FOOT = ParagraphStyle("f", fontName=F, size=16, leading=22, textColor=GREY)
TAG = ParagraphStyle("t", fontName=FB, size=18, textColor=ORANGE)


def slide(story, headline, lead, chart=None, proof=None, challenge=False):
    story.append(Paragraph("SWIGGY MARKET INTELLIGENCE" + ("  ·  %d/8" % (len(seen) + 1)), TAG))
    story.append(Spacer(1, 10))
    story.append(Paragraph(headline, HEAD_S if len(headline) > 42 else HEAD))
    story.append(Spacer(1, 8))
    story.append(Paragraph(lead, LEAD))
    story.append(Spacer(1, 18))
    if chart:
        iw = W - 195 * mm
        img = Image(str(CHARTS / chart), width=iw, height=iw * 0.505)
        story.append(img)
        story.append(Spacer(1, 8))
    if proof:
        story.append(Paragraph(proof, PROOF))
    story.append(Spacer(1, 6))
    story.append(Paragraph("Hrishit Prakash  ·  github.com/hrishitprakash2-debug", FOOT))
    seen.append(1)
    story.append(PageBreak())


def frame(canv, doc):
    canv.saveState()
    canv.setFillColor(ORANGE)
    canv.rect(0, H - 12, W, 12, stroke=0, fill=1)
    canv.setFillColor(colors.HexColor("#F4F4F4"))
    canv.rect(0, 0, W, 6, stroke=0, fill=1)
    canv.restoreState()


seen: list = []
doc = SimpleDocTemplate(str(OUT), pagesize=landscape((W, H)),
                        leftMargin=75 * mm / 4, rightMargin=75 * mm / 4,
                        topMargin=40, bottomMargin=24,
                        title="Swiggy Market Intelligence — findings")
story: list = []

# 1 — cover (two-column: statement left, supply chart right)
from reportlab.platypus import Table, TableStyle

left = [
    Paragraph("SWIGGY MARKET INTELLIGENCE", TAG),
    Spacer(1, 26),
    Paragraph("I analysed", ParagraphStyle("cv0", fontName=F, size=30, leading=34,
                                           textColor=GREY)),
    Paragraph("148,455", ParagraphStyle("cv1", fontName=FB, size=150, leading=150,
                                        textColor=ORANGE)),
    Paragraph("Swiggy restaurant<br/>listings.", ParagraphStyle(
        "cv2", fontName=FB, size=46, leading=52, textColor=INK)),
    Spacer(1, 22),
    Paragraph("Three findings that changed how I think<br/>about India's food-delivery market.",
              ParagraphStyle("cs", fontName=F, size=21, leading=30, textColor=GREY)),
    Spacer(1, 18),
    Paragraph("SQL  ·  PYTHON  ·  EXCEL", ParagraphStyle("tag3", fontName=FB, size=18,
                                                         textColor=INK)),
    Paragraph("No synthetic data · no machine learning", FOOT),
]

iw = 640
right = [
    Paragraph("Every listing, mapped", ParagraphStyle("rt", fontName=FB, size=17,
                                                      textColor=ORANGE)),
    Spacer(1, 6),
    Image(str(CHARTS / "01_supply_pareto.png"), width=iw, height=iw * 0.5055),
    Spacer(1, 10),
    Paragraph("Top 7 cities = 51.0% of national supply", ParagraphStyle(
        "rp", fontName=FB, size=17, textColor=INK)),
]

cover = Table([[left, right]], colWidths=[W - iw - 190, iw], rowHeights=[735])
cover.setStyle(TableStyle([
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("LEFTPADDING", (0, 0), (-1, -1), 0),
    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ("TOPPADDING", (0, 0), (-1, -1), 0),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ("LEFTPADDING", (1, 0), (1, 0), 40),
]))
_ch = cover.wrapOn(None, W, 1e6)[1]          # measured height, so the block is truly centred
story.append(Spacer(1, max(0, (H - 90 - _ch) / 2)))
story.append(cover)
seen.append(1)
story.append(PageBreak())

slide(story, "Half the market is<br/>seven cities.",
      "Bangalore alone holds 10.1% of national supply. The other 545 cities share the rest.",
      chart="01_supply_pareto.png",
      proof="Top 7 cities = 51.0% of all listings")

slide(story, "58.6% of listings<br/>have no rating at all.",
      "87,014 outlets can't appear in ranked discovery. Not closed — invisible.",
      chart="04_review_confidence.png",
      proof="Among rated outlets: 3.76★ under 50 reviews → 4.04★ at 200+")

slide(story, "Supply and satisfaction<br/>run in opposite directions.",
      "North Indian is 15.8% of supply at 3.81★. Ice Cream is a fraction of that at 4.29★.",
      chart="03_cuisine_supply_vs_rating.png",
      proof="The biggest cuisines are the least loved; the small ones sit above the line")

slide(story, "The 45-minute promise<br/>is fiction in most metros.",
      "Kolkata breaches it on 91% of outlets, with a 69-minute median quote.",
      chart="05_sla_by_city.png",
      proof="Kolkata 91% · Chennai 85% · Pune 75% · Ahmedabad 45%")

slide(story, "Speed is the one lever<br/>you can actually pull.",
      "Menu, price and cuisine are fixed once an outlet opens. Delivery time isn't.",
      chart="06_delivery_vs_rating.png",
      proof="≤40 min → 3.81★    75+ min → 3.44★")

slide(story, "So where would I<br/>open the next outlet?",
      "A composite score: 35% rating + 25% review depth + 20% price headroom + 20% low saturation.",
      chart="08_opportunity_localities.png",
      proof="#1 Kankurgachi, Kolkata — 27 outlets, 4.16★, 193 average reviews")

story.append(Paragraph("SWIGGY MARKET INTELLIGENCE  ·  8/8", TAG))
story.append(Spacer(1, 12))
story.append(Paragraph("Built end to end<br/>in SQL, Python and Excel.", HEAD))
story.append(Spacer(1, 20))
for line in ["SQLite star schema · 25 analytical queries (window functions, CTEs, HHI index)",
             "pandas cleaning with a documented data-quality log — no imputed values",
             "Excel dashboard where every figure is a live formula, recalculated and verified",
             "8-page report · 10 charts · full pipeline, reproducible end to end"]:
    story.append(Paragraph(f"•  {line}", ParagraphStyle("b", fontName=F, size=24, leading=38,
                                                        textColor=INK)))
story.append(Spacer(1, 24))
story.append(Paragraph("Repo and dashboard: github.com/hrishitprakash2-debug", PROOF))
story.append(Spacer(1, 10))
story.append(Paragraph("Data: 148,455 live Swiggy listings + 8,668 metro outlets with delivery times",
                       FOOT))
seen.append(1)

doc.build(story, onFirstPage=frame, onLaterPages=frame)
print(f"saved {OUT} ({OUT.stat().st_size/1e6:.2f} MB, {len(seen)} slides)")
