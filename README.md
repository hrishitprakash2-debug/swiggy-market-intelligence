# Swiggy Market Intelligence

**Where India's food-delivery supply is concentrated, what it charges, and why delivery speed is the one lever that moves ratings.**

An end-to-end analytics project on **148,455 real Swiggy restaurant listings** across **552 cities**, built in the three tools a data analyst is actually hired for: **SQL** for the warehouse and the analysis, **Python** for the pipeline and the visuals, **Excel** for the deliverable a business stakeholder will open.

<p align="left">
  <img alt="rows" src="https://img.shields.io/badge/listings-148%2C455-FC8019">
  <img alt="cities" src="https://img.shields.io/badge/cities-552-1A1A1A">
  <img alt="queries" src="https://img.shields.io/badge/SQL%20queries-25-1A1A1A">
  <img alt="tests" src="https://img.shields.io/badge/reconciliation-PASS-3FA66A">
</p>

---

## The questions

A marketplace operator has three decisions: **where to open**, **what to charge**, and **what to fix**. This project answers all three from supply-side data:

1. Which cities and localities are saturated, and which have proven demand with room to enter?
2. What does a meal for two cost across India, and does charging more buy a better rating?
3. How much of the supply base is invisible to customers because it has no rating?
4. Does delivery time actually show up in customer satisfaction?
5. Where should the next outlet open? (A composite score, no machine learning.)

## Findings

| # | Finding | Number |
|---|---|---|
| 1 | **Supply is extremely concentrated.** The top 7 cities hold half of all listings; Bangalore alone holds 10.1%. | 51.0% |
| 2 | **58.6% of all listings carry no rating at all** — they cannot appear in rank-based discovery. | 87,014 outlets |
| 3 | **Supply and satisfaction run in opposite directions.** North Indian is 15.8% of supply at 3.81★; Ice Cream is a fraction of that at 4.29★. | +0.48★ |
| 4 | **Ratings are earned, not inflated.** Average rating rises from 3.76★ (under 50 reviews) to 4.04★ (200+). | +0.29★ |
| 5 | **Delivery time is the strongest controllable driver of satisfaction.** ≤40 min averages 3.81★, 75+ min averages 3.44★. | −0.36★ |
| 6 | **Kolkata misses a 45-minute promise on 91% of outlets** (median quote 69 min); Ahmedabad on 45%. | 91.4% vs 44.7% |
| 7 | **Price stops buying satisfaction after the cheap end.** Ratings are flat from the cheapest decile to the ninth; only the top two deciles clear 3.95★. | plateau |
| 8 | **No city is dominated by one cuisine.** Cuisine HHI stays under 1,500 in every major market — competition is fragmented and price-led. | HHI < 1,500 |

**Full narrative:** [`output/Swiggy_Market_Intelligence_Report.pdf`](output/Swiggy_Market_Intelligence_Report.pdf) (8 pages)

## The data

Two real, publicly available extracts of Swiggy's own listings — **no synthetic, simulated or imputed data anywhere in the pipeline.**

| Table | Rows | Content |
|---|---|---|
| `swiggy_national.csv` | 148,541 | outlet name, city/locality, cost for two, star rating, review band, cuisines |
| `swiggy_metro_sla.csv` | 8,680 | 8 metros, adds **quoted delivery time** |

The raw data is deliberately messy, which is where most of the work went:

- ratings arrive as the string `"--"` when Swiggy suppresses them
- review counts arrive banded as `"100+ ratings"` / `"1K+ ratings"`
- cost arrives as `"₹ 200"`
- one listing quoted a cost for two of **₹300,350**
- one restaurant name contained a control character that broke the Excel writer

Every one of those is parsed explicitly, counted, and recorded in [`data/clean/data_quality.json`](data/clean/data_quality.json). **Nothing is imputed** — a suppressed rating stays null rather than being filled with a guess.

## Architecture

```
┌──────────────────┐   ┌───────────────────────┐   ┌──────────────────┐
│  Raw Swiggy CSVs │──▶│  01_clean.py          │──▶│ data/clean/*.csv │
│  157,221 rows    │   │  parse · validate · log│   │ data_quality.json│
└──────────────────┘   └───────────────────────┘   └────────┬─────────┘
                                                            │
                       ┌────────────────────────────────────┘
                       ▼
        ┌──────────────────────────────┐      ┌────────────────────────┐
        │  SQLite star schema          │─────▶│  25 SQL queries        │
        │  2 facts · 5 dims · bridge   │      │  → output/sql_results/ │
        └──────────────────────────────┘      └───────────┬────────────┘
                                                          │
                       ┌──────────────────────────────────┴─────────┐
                       ▼                                            ▼
        ┌──────────────────────────┐              ┌──────────────────────────┐
        │ 04_charts.py → 10 PNGs   │              │ 05_build_excel.py        │
        │ 07_report.py → PDF       │              │ live formulas + charts   │
        └──────────────────────────┘              │ 06_recalc_excel.py       │
                                                  │ verifies vs pandas       │
                                                  └──────────────────────────┘
```

**Star schema** (`sql/schema.sql`): `fact_listing`, `fact_metro_sla`, and dimensions for city, locality, cuisine, price band and review confidence, plus `bridge_listing_cuisine` so an outlet tagged *"Biryani, Mughlai"* is counted once per cuisine instead of being flattened to its first tag.

**The 25 queries** (`sql/queries/`) are written as if for review, not for a notebook: one business question per file, a header comment stating it, and the technique each one demonstrates —

| Technique | Queries |
|---|---|
| Window: `RANK` / `NTILE` / `PERCENT_RANK` | q02, q11, q12, q17, q18, q24, q25 |
| Running totals & Pareto | q02, q13 |
| Median via `ROW_NUMBER` (SQLite has no `PERCENTILE_CONT`) | q03, q20 |
| CTEs, multi-step aggregation | q04, q05, q15, q20 |
| `NOT EXISTS` / anti-join pattern | q15 |
| Conditional-aggregation pivot | q07, q10, q19 |
| Herfindahl-Hirschman concentration index | q04, q05 |
| Bayesian-weighted ranking (shrinkage) | q24 |
| Composite percentile scoring | q25 |

## The Excel deliverable

`output/Swiggy_Market_Intelligence.xlsx` — 8 sheets, **every figure a live formula** over the full 148,455-row data sheet (`COUNTIFS`, `AVERAGEIFS`, `RANK.EQ`, `COUNTBLANK`), not a pasted value. Change a row in `Data` and the dashboard moves.

- **Dashboard** — 6 KPI cards, 4 native Excel charts, and five insight sentences that are themselves formulas
- **City Matrix / Cuisine Matrix** — per-entity metrics with data bars and colour scales
- **Price Bands / SLA Matrix** — COUNTIFS matrices
- **Method & Quality** — the data-quality log and every definition used
- **Data / Data SLA** — the full source rows, frozen headers, autofilter on

Formulas are recalculated in real Excel (`06_recalc_excel.py`) so the cached values exist for viewers that don't calculate, then **read back and diffed against pandas — 10 of 10 metrics match.**

## Reproduce it

```bash
git clone https://github.com/hrishitprakash2-debug/swiggy-market-intelligence.git
cd swiggy-market-intelligence
pip install -r requirements.txt

python scripts/00_download_data.py   # fetch the raw CSVs
python scripts/01_clean.py           # profile, parse, validate, log
python scripts/02_build_db.py        # build + reconcile the star schema
python scripts/03_run_queries.py     # run all 25 queries → CSV + index
python scripts/04_charts.py          # 10 charts
python scripts/05_build_excel.py     # workbook with live formulas
python scripts/06_recalc_excel.py    # Excel COM recalc + pandas diff
python scripts/07_report.py          # 8-page PDF
python scripts/08_carousel.py        # 8-slide LinkedIn carousel
```

`06_recalc_excel.py` needs Windows + Excel (COM). Everything else is cross-platform.

## Deliverables

| File | What it is |
|---|---|
| `output/Swiggy_Market_Intelligence.xlsx` | Excel dashboard, live formulas, native charts |
| `output/Swiggy_Market_Intelligence_Report.pdf` | 8-page executive report |
| `output/sql_results/*.csv` | Result of every query, exported |
| `output/sql_findings.md` | Index of all 25 queries with previews |
| `output/Swiggy_Carousel.pdf` | 8-slide carousel for LinkedIn |
| `charts/*.png` | 10 charts, 1600×900, carousel-ready |

## Limitations

- Listing-level observations, **not orders or revenue** — nothing here measures demand directly; outlet density is a proxy for market attention, reasonable but not causal.
- The delivery-time findings cover **8 metros only** and should not be extrapolated nationally.
- Ratings are as published at scrape time and subject to Swiggy's own suppression rules.
- `cost_for_two` is a self-reported band, not a transaction value.

## Stack

`Python 3.14` · `pandas` · `numpy` · `matplotlib` · `seaborn` · `SQLite` (window functions, CTEs) · `openpyxl` + Excel COM · `reportlab`

---

**Hrishit Prakash** — [LinkedIn](https://linkedin.com/in/hrishit-prakash-7666a5328) · [GitHub](https://github.com/hrishitprakash2-debug) · hrishit4280@gmail.com
