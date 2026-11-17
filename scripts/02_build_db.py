"""
02_build_db.py — Load cleaned CSVs into a normalised SQLite star schema.

Creates data/swiggy.db from sql/schema.sql, then fills dimensions, the cuisine
bridge table and both fact tables. Ends with row-count reconciliation so the
warehouse is proven to hold exactly the cleaned rows, no more.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
CLEAN, SQL, DB = ROOT / "data" / "clean", ROOT / "sql", ROOT / "data" / "swiggy.db"

nat = pd.read_csv(CLEAN / "restaurants_clean.csv")
sla = pd.read_csv(CLEAN / "metro_sla_clean.csv")

con = sqlite3.connect(DB)
con.executescript((SQL / "schema.sql").read_text(encoding="utf-8"))
con.execute("PRAGMA foreign_keys = ON")

# ---------------------------------------------------------------- dimensions
cities = sorted(set(nat["city_name"]) | set(sla["city_name"]))
con.executemany("INSERT INTO dim_city(city_name) VALUES (?)", [(c,) for c in cities])
city_map = dict(con.execute("SELECT city_name, city_sk FROM dim_city"))

locs = sorted(set(zip(nat["locality"], nat["city_name"])) |
              set(zip(sla["locality"], sla["city_name"])))
con.executemany(
    "INSERT INTO dim_locality(locality_name, city_sk) VALUES (?,?)",
    [(l, city_map[c]) for l, c in locs],
)
loc_map = {(l, c): sk for l, c, sk in con.execute(
    "SELECT locality_name, city_sk, locality_sk FROM dim_locality")}
# locality_sk keyed straight off city_sk lookups
city_sk_of = {c: city_map[c] for c in cities}
loc_sk = {(l, c): loc_map[(l, city_sk_of[c])] for l, c in locs}

cuisines = set(nat["primary_cuisine"].dropna()) | set(sla["primary_cuisine"].dropna())
for c in nat["cuisine"].dropna():
    cuisines |= {x.strip().title() for x in str(c).split(",") if x.strip()}
cuisines = sorted(cuisines)
con.executemany("INSERT INTO dim_cuisine(cuisine_name) VALUES (?)", [(c,) for c in cuisines])
cuis_map = dict(con.execute("SELECT cuisine_name, cuisine_sk FROM dim_cuisine"))

bands = [("<=150", 1, 0, 150), ("151-250", 2, 151, 250), ("251-350", 3, 251, 350),
         ("351-500", 4, 351, 500), ("501-750", 5, 501, 750), ("750+", 6, 751, 999999)]
con.executemany("INSERT INTO dim_price_band(band_label, band_order, lower_inr, upper_inr) "
                "VALUES (?,?,?,?)", bands)
band_map = dict(con.execute("SELECT band_label, price_band_sk FROM dim_price_band"))

conf = [("No rating yet", 1, None), ("Low (<50)", 2, 0),
        ("Moderate (50-199)", 3, 50), ("High (200+)", 4, 200)]
con.executemany("INSERT INTO dim_review_confidence(confidence_label, confidence_order, min_reviews) "
                "VALUES (?,?,?)", [(a, b, c) for a, b, c in conf])
conf_map = dict(con.execute("SELECT confidence_label, confidence_sk FROM dim_review_confidence"))

# ------------------------------------------------------------------ fact rows
nat_fact = pd.DataFrame({
    "listing_id": nat["listing_id"],
    "restaurant": nat["restaurant"],
    "locality_sk": [loc_sk[(l, c)] for l, c in zip(nat["locality"], nat["city_name"])],
    "cuisine_sk": [cuis_map[c] for c in nat["primary_cuisine"]],
    "price_band_sk": [band_map.get(b) for b in nat["cost_band"].astype(str)],
    "confidence_sk": [conf_map[c] for c in nat["review_confidence"]],
    "cost_for_two": nat["cost_for_two"],
    "rating": nat["rating"],
    "rating_count": nat["rating_count"],
    "rating_band": nat["rating_band"].astype(str).replace("nan", None),
    "cuisine_count": nat["cuisine_count"],
})
nat_fact.to_sql("fact_listing", con, if_exists="append", index=False)

bridge = []
for lid, cs in zip(nat["listing_id"], nat["cuisine"].fillna("")):
    for c in {x.strip().title() for x in str(cs).split(",") if x.strip()}:
        bridge.append((int(lid), cuis_map[c]))
pd.DataFrame(bridge, columns=["listing_id", "cuisine_sk"]).drop_duplicates().to_sql(
    "bridge_listing_cuisine", con, if_exists="append", index=False)

sla_fact = pd.DataFrame({
    "listing_id": sla["listing_id"],
    "restaurant": sla["restaurant"],
    "locality_sk": [loc_sk[(l, c)] for l, c in zip(sla["locality"], sla["city_name"])],
    "cuisine_sk": [cuis_map.get(c) for c in sla["primary_cuisine"]],
    "price_for_two": sla["price_for_two"],
    "rating": sla["rating"],
    "rating_count": sla["rating_count"],
    "delivery_min": sla["delivery_min"],
    "sla_band": sla["sla_band"].astype(str).replace("nan", None),
})
sla_fact.to_sql("fact_metro_sla", con, if_exists="append", index=False)

con.commit()

# ------------------------------------------------------- reconciliation gates
checks = {
    "fact_listing_rows": con.execute("SELECT COUNT(*) FROM fact_listing").fetchone()[0],
    "clean_csv_rows": len(nat),
    "fact_sla_rows": con.execute("SELECT COUNT(*) FROM fact_metro_sla").fetchone()[0],
    "clean_sla_rows": len(sla),
    "bridge_rows": con.execute("SELECT COUNT(*) FROM bridge_listing_cuisine").fetchone()[0],
    "dim_city": con.execute("SELECT COUNT(*) FROM dim_city").fetchone()[0],
    "dim_locality": con.execute("SELECT COUNT(*) FROM dim_locality").fetchone()[0],
    "dim_cuisine": con.execute("SELECT COUNT(*) FROM dim_cuisine").fetchone()[0],
    "orphan_locality_fks": con.execute(
        "SELECT COUNT(*) FROM fact_listing f LEFT JOIN dim_locality l "
        "ON f.locality_sk=l.locality_sk WHERE l.locality_sk IS NULL").fetchone()[0],
    "orphan_cuisine_fks": con.execute(
        "SELECT COUNT(*) FROM fact_listing f LEFT JOIN dim_cuisine c "
        "ON f.cuisine_sk=c.cuisine_sk WHERE c.cuisine_sk IS NULL").fetchone()[0],
    "revenue_sanity_sum_cost": con.execute(
        "SELECT ROUND(SUM(cost_for_two),0) FROM fact_listing").fetchone()[0],
}
for k, v in checks.items():
    print(f"  {k:<24} {v:>10,}" if isinstance(v, int) else f"  {k:<24} {v:>10}")

ok = (checks["fact_listing_rows"] == checks["clean_csv_rows"]
      and checks["fact_sla_rows"] == checks["clean_sla_rows"]
      and checks["orphan_locality_fks"] == 0 and checks["orphan_cuisine_fks"] == 0)
print("\nwarehouse reconciliation:", "PASS" if ok else "FAIL")
con.close()
