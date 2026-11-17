-- ============================================================================
--  Swiggy Market Intelligence — star schema (SQLite)
--  Grain: one row per unique restaurant listing on Swiggy.
--  Dimensions are surrogate-keyed so every fact join is a plain integer join.
-- ============================================================================

DROP TABLE IF EXISTS fact_listing;
DROP TABLE IF EXISTS fact_metro_sla;
DROP TABLE IF EXISTS bridge_listing_cuisine;
DROP TABLE IF EXISTS dim_city;
DROP TABLE IF EXISTS dim_locality;
DROP TABLE IF EXISTS dim_cuisine;
DROP TABLE IF EXISTS dim_price_band;
DROP TABLE IF EXISTS dim_review_confidence;

CREATE TABLE dim_city (
    city_sk      INTEGER PRIMARY KEY,
    city_name    TEXT NOT NULL UNIQUE
);

CREATE TABLE dim_locality (
    locality_sk  INTEGER PRIMARY KEY,
    locality_name TEXT NOT NULL,
    city_sk      INTEGER NOT NULL REFERENCES dim_city(city_sk),
    UNIQUE (locality_name, city_sk)
);

CREATE TABLE dim_cuisine (
    cuisine_sk   INTEGER PRIMARY KEY,
    cuisine_name TEXT NOT NULL UNIQUE
);

CREATE TABLE dim_price_band (
    price_band_sk INTEGER PRIMARY KEY,
    band_label    TEXT NOT NULL,
    band_order    INTEGER NOT NULL,
    lower_inr     INTEGER,
    upper_inr     INTEGER
);

CREATE TABLE dim_review_confidence (
    confidence_sk INTEGER PRIMARY KEY,
    confidence_label TEXT NOT NULL,
    confidence_order INTEGER NOT NULL,
    min_reviews   INTEGER
);

-- Many-to-many: a listing offers 1..n cuisines (comma-separated on the source).
CREATE TABLE bridge_listing_cuisine (
    listing_id INTEGER NOT NULL,
    cuisine_sk INTEGER NOT NULL REFERENCES dim_cuisine(cuisine_sk),
    PRIMARY KEY (listing_id, cuisine_sk)
);

CREATE TABLE fact_listing (
    listing_id    INTEGER PRIMARY KEY,
    restaurant    TEXT NOT NULL,
    locality_sk   INTEGER NOT NULL REFERENCES dim_locality(locality_sk),
    cuisine_sk    INTEGER NOT NULL REFERENCES dim_cuisine(cuisine_sk),   -- primary cuisine
    price_band_sk INTEGER REFERENCES dim_price_band(price_band_sk),
    confidence_sk INTEGER REFERENCES dim_review_confidence(confidence_sk),
    cost_for_two  REAL,        -- INR, NULL when unparseable
    rating        REAL,        -- 0-5, NULL when Swiggy suppresses it
    rating_count  INTEGER,     -- NULL = "Too Few Ratings"
    rating_band   TEXT,        -- derived bucket, kept for Excel parity
    cuisine_count INTEGER      -- how many cuisines the outlet serves
);

-- Operations layer: 8 metro cities, includes quoted delivery time.
CREATE TABLE fact_metro_sla (
    listing_id    INTEGER PRIMARY KEY,
    restaurant    TEXT NOT NULL,
    locality_sk   INTEGER NOT NULL REFERENCES dim_locality(locality_sk),
    cuisine_sk    INTEGER REFERENCES dim_cuisine(cuisine_sk),
    price_for_two REAL,
    rating        REAL,
    rating_count  INTEGER,
    delivery_min  REAL,
    sla_band      TEXT
);

CREATE INDEX idx_fact_locality  ON fact_listing(locality_sk);
CREATE INDEX idx_fact_cuisine   ON fact_listing(cuisine_sk);
CREATE INDEX idx_fact_priceband ON fact_listing(price_band_sk);
CREATE INDEX idx_fact_rating    ON fact_listing(rating);
CREATE INDEX idx_bridge_cuisine ON bridge_listing_cuisine(cuisine_sk);
CREATE INDEX idx_sla_city       ON fact_metro_sla(locality_sk);
CREATE INDEX idx_sla_delivery   ON fact_metro_sla(delivery_min);
