"""
04_charts.py — Every chart in the report and the carousel, built from SQL output.

Reads output/sql_results/*.csv (never the raw data) so a chart and the number
quoted beside it can never disagree. Saves 1600x900 PNGs to charts/.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.ticker import FuncFormatter

ROOT = Path(__file__).resolve().parent.parent
RES, OUT = ROOT / "output" / "sql_results", ROOT / "charts"
OUT.mkdir(exist_ok=True)

ORANGE, INK, GREY, ACCENT = "#FC8019", "#1A1A1A", "#8A8A8A", "#2E5AAC"
PALETTE = ["#FC8019", "#2E5AAC", "#3FA66A", "#B5452C", "#7A5AA6", "#C9A227"]

plt.rcParams.update({
    "figure.facecolor": "white", "axes.facecolor": "white",
    "axes.edgecolor": "#DDDDDD", "axes.labelcolor": INK,
    "text.color": INK, "xtick.color": GREY, "ytick.color": GREY,
    "font.size": 11, "axes.titlesize": 15, "axes.titleweight": "bold",
    "axes.spines.top": False, "axes.spines.right": False,
    "figure.dpi": 160, "savefig.bbox": "tight", "savefig.pad_inches": 0.35,
})
sns.set_palette(PALETTE)


def q(name: str) -> pd.DataFrame:
    return pd.read_csv(RES / f"{name}.csv")


def finish(fig, path: Path, subtitle: str = ""):
    if subtitle:
        fig.text(0.5, -0.02, subtitle, ha="center", fontsize=9.5, color=GREY)
    fig.savefig(path)
    plt.close(fig)
    print("  chart ->", path.name)


def inr(v, _=None):
    return f"₹{v:,.0f}"


# 1 ----------------------------------------------------------------- supply pareto
d = q("q02_city_supply_share").head(15)
fig, ax = plt.subplots(figsize=(12, 6.2))
ax.bar(d["city_name"], d["listings"], color=ORANGE, alpha=.9)
ax.set_ylabel("Restaurant listings")
ax.set_title("Seven cities hold half of India's Swiggy supply")
ax.tick_params(axis="x", rotation=35)
for i, (v, c) in enumerate(zip(d["listings"], d["cumulative_pct"])):
    ax.text(i, v + 180, f"{v/1000:.1f}k", ha="center", fontsize=8.5, color=INK)
ax2 = ax.twinx()
ax2.plot(d["city_name"], d["cumulative_pct"], color=ACCENT, marker="o", lw=2.2)
ax2.axhline(50, ls="--", color=GREY, lw=1)
ax2.set_ylabel("Cumulative % of national supply", color=ACCENT)
ax2.set_ylim(0, 105)
ax2.spines["right"].set_visible(True)
ax2.tick_params(colors=ACCENT)
finish(fig, OUT / "01_supply_pareto.png",
       "Source: 148,455 live Swiggy listings · cumulative share line reads on the right axis")

# 2 -------------------------------------------------------------- price index
d = q("q03_city_price_index")
hi, lo = d.head(8), d.tail(8)
sel = pd.concat([hi, lo]).drop_duplicates("city_name").sort_values("price_index_national_1x")
colors = [ORANGE if v > 1 else ACCENT for v in sel["price_index_national_1x"]]
fig, ax = plt.subplots(figsize=(11, 6.4))
ax.barh(sel["city_name"], sel["price_index_national_1x"], color=colors, alpha=.9)
ax.axvline(1.0, color=INK, lw=1.5, ls="--")
ax.text(1.01, -0.6, "national median", fontsize=9, color=INK)
ax.set_xlabel("Median cost for two, indexed to national median (1.0×)")
ax.set_title("What a meal for two costs, city by city")
finish(fig, OUT / "02_price_index.png",
       "Median (not mean) cost for two per city, min 150 listings · national median ₹250")

# 3 --------------------------------------------------- cuisine supply vs rating
d = q("q06_cuisine_performance").copy()
d["pct_of_supply"] = pd.to_numeric(d["pct_of_supply"])
fig, ax = plt.subplots(figsize=(11, 6.6))
sc = ax.scatter(d["pct_of_supply"], d["avg_rating"], s=d["avg_reviews"] * 1.8,
                c=[ORANGE if r >= 4.0 else ACCENT for r in d["avg_rating"]],
                alpha=.65, edgecolor="white", linewidth=1.4)
ax.axhline(d["avg_rating"].mean(), ls="--", color=GREY, lw=1)
ax.set_xlabel("% of national supply (primary cuisine)")
ax.set_ylabel("Average rating")
ax.set_title("Supply is not satisfaction: the biggest cuisines do not rate best")
for _, r in d.iterrows():
    if r["pct_of_supply"] > 4.5 or r["avg_rating"] > 4.05 or r["avg_rating"] < 3.75:
        ax.annotate(r["primary_cuisine"], (r["pct_of_supply"], r["avg_rating"]),
                    fontsize=8.5, xytext=(5, 4), textcoords="offset points")
finish(fig, OUT / "03_cuisine_supply_vs_rating.png",
       "Bubble size = average review volume · cuisines with 400+ listings")

# 4 ------------------------------------------------ review confidence ladder
d = q("q08_review_confidence").dropna(subset=["avg_rating"])
fig, ax = plt.subplots(figsize=(10.5, 5.8))
bars = ax.bar(d["confidence_label"], d["avg_rating"], color=PALETTE[:len(d)], alpha=.9)
ax.set_ylim(3.4, 4.2)
ax.set_ylabel("Average rating")
ax.set_title("Ratings are earned: outlets with more reviews rate higher")
for b, (_, r) in zip(bars, d.iterrows()):
    ax.text(b.get_x() + b.get_width()/2, b.get_height() + .012,
            f"{r['avg_rating']:.3f}\n{int(r['listings']):,} outlets",
            ha="center", fontsize=9)
ax.set_xlabel("Review volume band")
finish(fig, OUT / "04_review_confidence.png",
       "58.6% of all listings carry no rating at all and are excluded here")

# 5 ------------------------------------------------------------ SLA by metro
d = q("q20_sla_city").sort_values("median_delivery_min")
fig, ax = plt.subplots(figsize=(11.5, 6))
bars = ax.barh(d["city_name"], d["median_delivery_min"], color=ORANGE, alpha=.9)
ax.axvline(45, color=ACCENT, ls="--", lw=1.6)
ax.text(45.5, -0.55, "45-min promise", color=ACCENT, fontsize=9)
for b, (_, r) in zip(bars, d.iterrows()):
    ax.text(b.get_width() + .7, b.get_y() + b.get_height()/2,
            f"{r['median_delivery_min']:.0f} min · {r['pct_breach_45min']:.0f}% breach",
            va="center", fontsize=9)
ax.set_xlim(0, 88)
ax.set_xlabel("Median delivery time (minutes)")
ax.set_title("Kolkata misses a 45-minute promise on 9 of every 10 orders")
finish(fig, OUT / "05_sla_by_city.png",
       "8,668 metro outlets with published delivery times · breach = quoted time above 45 min")

# 6 ------------------------------------------------- delivery band vs rating
d = q("q21_sla_rating_relation")
fig, ax = plt.subplots(figsize=(10.5, 5.8))
ax.plot(d["sla_band"], d["avg_rating"], marker="o", ms=9, lw=2.6, color=ORANGE)
for x, y in zip(d["sla_band"], d["avg_rating"]):
    ax.annotate(f"{y:.2f}", (x, y), textcoords="offset points", xytext=(0, 10),
                ha="center", fontsize=9.5)
ax.set_ylim(3.35, 3.9)
ax.set_ylabel("Average rating")
ax.set_xlabel("Quoted delivery window")
ax.set_title("Every extra 15 minutes of delivery time costs roughly 0.1 stars")
finish(fig, OUT / "06_delivery_vs_rating.png",
       "Metro dataset · 8,668 outlets")

# 7 ---------------------------------------------------- price decile vs rating
d = q("q12_price_decile_rating")
fig, ax = plt.subplots(figsize=(10.5, 5.8))
ax.bar(d["price_decile"].astype(str), d["avg_rating"], color=ACCENT, alpha=.85)
ax.set_ylim(3.7, 4.12)
ax.set_xlabel("Price decile (1 = cheapest)")
ax.set_ylabel("Average rating")
ax.set_title("Charging more buys a better rating — but only in the top two deciles")
for x, (v, p) in enumerate(zip(d["avg_rating"], d["pct_unrated"])):
    ax.text(x, v + .004, f"{v:.2f}", ha="center", fontsize=9)
finish(fig, OUT / "07_price_decile_rating.png",
       "Deciles of cost for two across 148k listings · ratings plateau until decile 9")

# 8 ----------------------------------------------------- opportunity localities
d = q("q25_locality_opportunity_score").head(12).iloc[::-1]
fig, ax = plt.subplots(figsize=(11, 6.4))
ax.barh([f"{r.locality_name} · {r.city_name}" for r in d.itertuples()],
        d["opportunity_score"], color=ORANGE, alpha=.9)
for y, (score, r) in enumerate(zip(d["opportunity_score"], d["avg_rating"])):
    ax.text(score + 1, y, f"{score:.0f} · {r:.2f}★", va="center", fontsize=9)
ax.set_xlim(0, 105)
ax.set_xlabel("Opportunity score (0-100 composite)")
ax.set_title("Where the next outlet should open")
finish(fig, OUT / "08_opportunity_localities.png",
       "Score = 35% rating + 25% review depth + 20% price headroom + 20% low saturation")

# 9 ------------------------------------------------- cuisine x price heatmap
d = q("q07_cuisine_price_matrix").head(14).set_index("cuisine_name")
cols = [c for c in d.columns if c.startswith("b_")]
mat = d[cols].div(d["listings"], axis=0) * 100
fig, ax = plt.subplots(figsize=(11.5, 7))
sns.heatmap(mat, annot=True, fmt=".0f", cmap="Oranges", cbar_kws={"label": "% of cuisine's outlets"},
            linewidths=.6, linecolor="white", ax=ax)
ax.set_xticklabels([c.replace("b_", "").replace("_", "-") + " ₹" for c in cols], rotation=0)
ax.set_ylabel("")
ax.set_title("Where each cuisine actually competes on price (% of outlets)")
finish(fig, OUT / "09_cuisine_price_heatmap.png",
       "Row percentages · cuisines with 400+ listings")

# 10 ------------------------------------------------ rating bands stacked
d = q("q10_rating_band_by_city").head(12)
bands = ["rb_upto_3_0", "rb_3_1_3_5", "rb_3_6_4_0", "rb_4_1_4_5", "rb_4_6_5_0"]
labels = ["≤3.0", "3.1-3.5", "3.6-4.0", "4.1-4.5", "4.6-5.0"]
share = d[bands].div(d[bands].sum(axis=1), axis=0) * 100
fig, ax = plt.subplots(figsize=(12, 6.2))
bottom = np.zeros(len(d))
for b, lab, c in zip(bands, labels, ["#B5452C", "#D98032", "#EDBB57", "#7FA86A", "#3FA66A"]):
    ax.barh(d["city_name"], share[b], left=bottom, label=lab, color=c)
    bottom += share[b].values
ax.set_xlim(0, 100)
ax.set_xlabel("% of rated outlets in each rating band")
ax.set_title("Quality spread: every big city has a 15-25% tail below 3.5 stars")
ax.legend(ncol=5, fontsize=8.5, loc="upper center", bbox_to_anchor=(.5, -.12), frameon=False)
ax.invert_yaxis()
finish(fig, OUT / "10_rating_bands_by_city.png",
       "Rated outlets only · cities with 150+ listings")

print(f"\n{len(list(OUT.glob('*.png')))} charts written to charts/")
