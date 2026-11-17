-- Q18 | City rating gap vs the national average (window aggregate, no subquery)
-- Business question: which cities over- or under-deliver on satisfaction?
WITH city AS (
    SELECT c.city_name, COUNT(*) AS listings, AVG(f.rating) AS avg_rating
    FROM fact_listing f
    JOIN dim_locality l ON l.locality_sk = f.locality_sk
    JOIN dim_city     c ON c.city_sk     = l.city_sk
    WHERE f.rating IS NOT NULL
    GROUP BY c.city_name
)
SELECT
    city_name,
    listings,
    ROUND(avg_rating, 3)                                                   AS avg_rating,
    ROUND(AVG(avg_rating) OVER (), 3)                                      AS national_avg_rating,
    ROUND(avg_rating - AVG(avg_rating) OVER (), 3)                         AS gap_vs_national,
    RANK() OVER (ORDER BY avg_rating DESC)                                 AS rank_by_rating
FROM city
WHERE listings >= 150
ORDER BY avg_rating DESC;
