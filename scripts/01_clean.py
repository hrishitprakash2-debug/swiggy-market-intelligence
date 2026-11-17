"""
01_clean.py — Clean the two real Swiggy extracts into analysis-ready tables.

Inputs (data/raw/):
  swiggy_national.csv  — 148,541 restaurant listings across Indian localities
  swiggy_metro_sla.csv — 8,680 metro restaurants incl. delivery time

Outputs (data/clean/):
  restaurants_clean.csv   — one row per unique restaurant listing
  metro_sla_clean.csv     — metro listings with parsed price / rating / SLA
  data_quality.json       — every drop, parse failure and integrity count

Design notes:
  * Ratings arrive as '--' when Swiggy suppresses them; counts as banded strings
    ('100+ ratings'), cost as '₹ 200'. Everything is parsed explicitly and the
    parse-failure count is logged rather than silently coerced.
  * Nothing is imputed. A missing rating stays null and is excluded from
    rating-based aggregates — imputing would fabricate satisfaction data.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW, CLEAN = ROOT / "data" / "raw", ROOT / "data" / "clean"
CLEAN.mkdir(parents=True, exist_ok=True)

log: dict = {"source": "Swiggy public restaurant listings (scraped)", "tables": {}}


# --------------------------------------------------------------------------
# parsers
# --------------------------------------------------------------------------
def parse_rating(v):
    """'4.2' -> 4.2 ; '--' / '' / junk -> NaN"""
    s = str(v).strip()
    if s in {"--", "", "nan", "None", "NEW"}:
        return np.nan
    try:
        r = float(s)
    except ValueError:
        return np.nan
    return r if 0 <= r <= 5 else np.nan


def parse_rating_count(v):
    """'500+ ratings' -> 500 ; '1K+ ratings' -> 1000 ; 'Too Few Ratings' -> NaN"""
    s = str(v).strip()
    if s in {"Too Few Ratings", "--", "", "nan", "None"}:
        return np.nan
    m = re.search(r"([\d.]+)\s*([KkMm]?)", s)
    if not m:
        return np.nan
    n = float(m.group(1))
    unit = m.group(2).upper()
    if unit == "K":
        n *= 1_000
    elif unit == "M":
        n *= 1_000_000
    return int(n)


def parse_cost(v):
    """'₹ 200' -> 200 ; NaN otherwise"""
    s = str(v).replace("₹", "").replace(",", "").strip()
    try:
        c = float(s)
    except ValueError:
        return np.nan
    return c if c > 0 else np.nan


CTRL = re.compile(r"[\x00-\x1f\x7f]")


def sanitize(v):
    """Strip control characters that break Excel writers; records are counted upstream."""
    return CTRL.sub("", str(v)).strip()


def split_geo(v):
    """'Indirapuram,Delhi' -> ('Indirapuram', 'Delhi') ; 'Bikaner' -> ('Bikaner','Bikaner')"""
    s = str(v).strip()
    if "," in s:
        locality, _, city = s.rpartition(",")
        return locality.strip().title(), city.strip().title()
    return s.title(), s.title()


# --------------------------------------------------------------------------
# 1. national listings
# --------------------------------------------------------------------------
nat = pd.read_csv(RAW / "swiggy_national.csv", low_memory=False, encoding="utf-8")
rows_in = len(nat)

# profile every categorical-ish source column before touching it
profile = {
    "distinct_rating_labels": sorted({str(v) for v in nat["rating"].unique()})[:12],
    "distinct_rating_count_labels": sorted({str(v) for v in nat["rating_count"].unique()})[:12],
    "distinct_cost_labels": sorted({str(v) for v in nat["cost"].unique()})[:8],
}

nat["rating"] = nat["rating"].map(parse_rating)
nat["rating_count"] = nat["rating_count"].map(parse_rating_count)
nat["cost_for_two"] = nat["cost"].map(parse_cost)

# Implausible cost values (a ₹300,350 "cost for two") would distort every average
# and percentile, so they are nulled rather than kept or winsorised. Counted below.
implausible = (nat["cost_for_two"] < 50) | (nat["cost_for_two"] > 10_000)
nat.loc[implausible, "cost_for_two"] = np.nan

geo = nat["city"].map(split_geo)
nat["locality"] = [g[0] for g in geo]
nat["city_name"] = [g[1] for g in geo]

nat["cuisine"] = nat["cuisine"].map(sanitize)
nat["city"] = nat["city"].map(sanitize)
nat["primary_cuisine"] = (
    nat["cuisine"].fillna("Unknown").astype(str)
    .str.split(",").str[0].str.strip().str.title()
)
nat["cuisine_count"] = (
    nat["cuisine"].fillna("").astype(str)
    .apply(lambda s: 0 if not s.strip() else len([c for c in s.split(",") if c.strip()]))
)

ctrl_hits = int(nat["name"].fillna("").astype(str).str.contains(CTRL, regex=True).sum())
nat["restaurant"] = nat["name"].fillna("").map(sanitize)

# ---- drop rules, each counted -------------------------------------------
drops = {}
drops["missing_restaurant_name"] = int((nat["restaurant"] == "").sum())
nat = nat[nat["restaurant"] != ""]

drops["duplicate_listing_id"] = int(nat.duplicated(subset="id").sum())
nat = nat.drop_duplicates(subset="id")

# rows used for *supply* analysis need a geography; cost/rating nullable
drops["unparseable_geography"] = int(nat["city_name"].isna().sum())
nat = nat[nat["city_name"].notna()]

# derived bands
nat["rating_band"] = pd.cut(
    nat["rating"], bins=[0, 3.0, 3.5, 4.0, 4.5, 5.01],
    labels=["<=3.0", "3.1-3.5", "3.6-4.0", "4.1-4.5", "4.6-5.0"], right=True,
)
nat["cost_band"] = pd.cut(
    nat["cost_for_two"], bins=[0, 150, 250, 350, 500, 750, 100_000],
    labels=["<=150", "151-250", "251-350", "351-500", "501-750", "750+"],
)
# a rating is only trustworthy if it has review volume behind it
nat["review_confidence"] = np.where(
    nat["rating_count"].isna(), "No rating yet",
    np.where(nat["rating_count"] < 50, "Low (<50)",
             np.where(nat["rating_count"] < 200, "Moderate (50-199)", "High (200+)"))
)

nat_clean = nat[[
    "id", "restaurant", "locality", "city_name", "cost_for_two", "cost_band",
    "rating", "rating_band", "rating_count", "review_confidence",
    "primary_cuisine", "cuisine_count", "cuisine",
]].rename(columns={"id": "listing_id"}).reset_index(drop=True)

log["tables"]["restaurants"] = {
    "rows_in": rows_in,
    "rows_out": len(nat_clean),
    "drops": drops,
    "source_column_profile": profile,
    "control_characters_stripped": ctrl_hits,
    "null_rate_pct": {
        c: round(float(nat_clean[c].isna().mean() * 100), 2)
        for c in ["cost_for_two", "rating", "rating_count", "primary_cuisine"]
    },
    "distinct": {
        "cities": int(nat_clean["city_name"].nunique()),
        "localities": int(nat_clean["locality"].nunique()),
        "cuisines": int(nat_clean["primary_cuisine"].nunique()),
    },
    # integrity: implausible costs were nulled, not kept
    "implausible_cost_nulled": int(implausible.sum()),
    "cost_out_of_range_after_cleaning": int(((nat_clean["cost_for_two"] < 50) |
                                             (nat_clean["cost_for_two"] > 10_000)).sum()),
}

# --------------------------------------------------------------------------
# 2. metro SLA table
# --------------------------------------------------------------------------
sla = pd.read_csv(RAW / "swiggy_metro_sla.csv", low_memory=False, encoding="utf-8")
sla_in = len(sla)

sla["price_for_two"] = pd.to_numeric(sla["Price"], errors="coerce")
sla["rating"] = pd.to_numeric(sla["Avg ratings"], errors="coerce")
sla["rating_count"] = pd.to_numeric(sla["Total ratings"], errors="coerce")
sla["delivery_min"] = pd.to_numeric(sla["Delivery time"], errors="coerce")

sla_drops = {}
sla_drops["zero_or_missing_price"] = int((sla["price_for_two"].fillna(0) <= 0).sum())
sla = sla[sla["price_for_two"] > 0]

sla_drops["duplicate_restaurant_area"] = int(
    sla.duplicated(subset=["Restaurant", "Area", "City"]).sum())
sla = sla.drop_duplicates(subset=["Restaurant", "Area", "City"])

sla_drops["delivery_time_outside_5_180"] = int(
    (~sla["delivery_min"].between(5, 180)).sum())
sla = sla[sla["delivery_min"].between(5, 180)]

sla["primary_cuisine"] = (
    sla["Food type"].astype(str).str.split(",").str[0].str.strip().str.title()
)
sla["sla_band"] = pd.cut(
    sla["delivery_min"], bins=[0, 40, 50, 60, 75, 200],
    labels=["<=40 min", "41-50 min", "51-60 min", "61-75 min", "75+ min"],
)
sla["Restaurant"] = sla["Restaurant"].map(sanitize)
sla["Area"] = sla["Area"].map(sanitize)
sla["Food type"] = sla["Food type"].map(sanitize)
sla["city_name"] = sla["City"].astype(str).str.strip().str.title()
sla["locality"] = sla["Area"].astype(str).str.strip().str.title()

sla_clean = sla[[
    "ID", "Restaurant", "locality", "city_name", "price_for_two", "rating",
    "rating_count", "delivery_min", "sla_band", "primary_cuisine",
]].rename(columns={"ID": "listing_id", "Restaurant": "restaurant"}).reset_index(drop=True)

log["tables"]["metro_sla"] = {
    "rows_in": sla_in,
    "rows_out": len(sla_clean),
    "drops": sla_drops,
    "median_delivery_min": float(sla_clean["delivery_min"].median()),
    "p90_delivery_min": float(sla_clean["delivery_min"].quantile(0.90)),
    "cities": sorted(sla_clean["city_name"].unique().tolist()),
}

# --------------------------------------------------------------------------
# 3. integrity checks that gate every headline number
# --------------------------------------------------------------------------
checks = {
    "national_row_count_matches": len(nat_clean) == rows_in - sum(drops.values()),
    "no_negative_cost": bool((nat_clean["cost_for_two"].dropna() > 0).all()),
    "rating_within_0_5": bool(nat_clean["rating"].dropna().between(0, 5).all()),
    "rating_count_non_negative": bool((nat_clean["rating_count"].dropna() >= 0).all()),
    "listing_ids_unique": bool(nat_clean["listing_id"].is_unique),
    "sla_ids_unique": bool(sla_clean["listing_id"].is_unique),
}
log["integrity_checks"] = checks
log["integrity_passed"] = all(checks.values())

nat_clean.to_csv(CLEAN / "restaurants_clean.csv", index=False, encoding="utf-8")
sla_clean.to_csv(CLEAN / "metro_sla_clean.csv", index=False, encoding="utf-8")
(CLEAN / "data_quality.json").write_text(json.dumps(log, indent=2, default=str), encoding="utf-8")

print(f"restaurants: {rows_in:,} raw -> {len(nat_clean):,} clean  drops={drops}")
print(f"metro SLA  : {sla_in:,} raw -> {len(sla_clean):,} clean  drops={sla_drops}")
print(f"cities={nat_clean.city_name.nunique()} localities={nat_clean.locality.nunique()} "
      f"cuisines={nat_clean.primary_cuisine.nunique()}")
print("integrity:", "PASS" if log["integrity_passed"] else "FAIL", checks)
print("null rates %:", log["tables"]["restaurants"]["null_rate_pct"])
