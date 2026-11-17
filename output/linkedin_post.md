# LinkedIn launch pack

## Post (copy-paste)

> I scraped 148,000 restaurant listings off Swiggy to answer one question: **where does a food business actually stand a chance?**
>
> Three things surprised me.
>
> **1. Half the country is served by seven cities.**
> Bangalore alone holds 10.1% of all supply. The other 545 cities share the other half.
>
> **2. 58.6% of listings have no rating at all.**
> 87,014 outlets. Not bad restaurants — invisible ones. Swiggy withholds a star rating until you cross a review threshold, so the majority of the marketplace can't appear in ranked discovery.
>
> **3. Delivery speed beats price.**
> Outlets quoting under 40 minutes average 3.81★. Over 75 minutes: 3.44★.
> Meanwhile price barely matters — ratings are flat from the cheapest decile to the ninth. Charging ₹400 instead of ₹200 buys you 0.16 stars.
>
> Kolkata misses a 45-minute promise on **91%** of its outlets. Ahmedabad, on 45%. Same country, same promise.
>
> So I built the whole thing end to end:
> → **SQL**: SQLite star schema, 25 queries — window functions, CTEs, an HHI concentration index
> → **Python**: pandas cleaning (ratings stored as "--", counts as "100+ ratings", a ₹300,350 meal for two), 10 charts
> → **Excel**: every figure a live COUNTIFS/AVERAGEIFS formula over 148k rows, not a pasted value — recalculated in Excel and diffed against pandas, 10/10 match
>
> No machine learning. No synthetic data. Just cleaning, querying, and finding the story.
>
> Full repo (code + dashboard + 8-page report): [link in comments]
>
> What would you analyse next — cuisine saturation, or delivery radius?
>
> #DataAnalytics #SQL #Python #Excel #DataVisualization #BusinessAnalytics #Portfolio #OpenToWork

---

## Carousel — 8 slides (1600×900, PDF)

| Slide | Image | Copy |
|---|---|---|
| 1 | cover card | **I analysed 148,455 Swiggy listings.**<br>3 findings that changed how I think about food delivery. |
| 2 | `charts/01_supply_pareto.png` | **Half the market is 7 cities.**<br>Bangalore 10.1% · Delhi 9.5% · Pune 8.4%<br><br>The other 545 cities share the rest. |
| 3 | `charts/04_review_confidence.png` | **58.6% of listings have no rating.**<br><br>87,014 outlets can't appear in ranked discovery.<br>Among those that are rated, more reviews = higher stars (3.76 → 4.04). |
| 4 | `charts/03_cuisine_supply_vs_rating.png` | **Supply ≠ satisfaction.**<br><br>North Indian: 15.8% of supply, 3.81★<br>Ice Cream: a fraction of the supply, 4.29★<br><br>Big cuisines compete on price. Small ones win on rating. |
| 5 | `charts/05_sla_by_city.png` | **The 45-minute promise is fiction in 6 of 8 metros.**<br><br>Kolkata: 91% breach, 69-min median.<br>Ahmedabad: 45%. |
| 6 | `charts/06_delivery_vs_rating.png` | **Speed is the only lever you can actually pull.**<br><br>≤40 min → 3.81★<br>75+ min → 3.44★<br><br>Menu, price and cuisine are fixed once you open. |
| 7 | `charts/08_opportunity_localities.png` | **Where I'd open next.**<br><br>A composite score: 35% rating, 25% review depth, 20% price headroom, 20% low saturation.<br><br>#1: Kankurgachi, Kolkata. |
| 8 | `charts/09_cuisine_price_heatmap.png` | **Built with SQL + Python + Excel.**<br><br>Star schema · 25 queries · 10 charts · live-formula dashboard · 8-page report<br><br>Repo in comments. |

---

## Alternative hooks (pick one)

1. "58.6% of restaurants on Swiggy are invisible. Not closed — invisible. Here's what 148,455 listings told me."
2. "I built a data project on Swiggy. My first query killed my assumption: the biggest cuisine is nowhere near the best-rated."
3. "Every food business thinks price drives ratings. The data says delivery time does — and the gap is 0.37 stars."

## First comment (post it yourself, immediately)

> Repo with all the code, the SQL queries and the Excel dashboard: https://github.com/hrishitprakash/swiggy-market-intelligence
>
> Pipeline: raw scrape → cleaning with a documented quality log → SQLite star schema → 25 SQL queries → 10 charts → Excel dashboard (live formulas) → PDF report.
>
> Data is real Swiggy listing data — no synthetic numbers. Ratings, review counts and costs came in as text ("--", "100+ ratings", "₹ 200") and are parsed explicitly, with every drop counted.

## Replies to expected comments

**"How did you get the data?"**
> Public scraped extracts of Swiggy listings (Hugging Face datasets). Listing-level, so no orders or revenue — supply-side only. That's in the limitations section of the report.

**"Why no ML?"**
> Deliberate. Churn or demand forecasting needs order history, which isn't public. On listing data, segmentation and SQL analysis answer the business question honestly rather than dressing up a model that can't be validated.

**"Can you share the Excel?"**
> Yes — it's in the repo under output/. Every number is a live formula over the 148k-row data sheet, so you can change a row and watch the dashboard move.

---

## Posting checklist

- [ ] Upload carousel as PDF (8 slides, 1600×900 each) — LinkedIn renders PDFs as swipeable docs
- [ ] Post between Tue–Thu, 8–10 am IST
- [ ] Put the repo link in the first comment, not the post body (reach)
- [ ] Reply to every comment in the first 90 minutes
- [ ] Pin the post to your profile for the internship season
- [ ] Add the repo link to your resume and LinkedIn "Featured" section
