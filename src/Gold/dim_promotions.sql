DROP TABLE IF EXISTS gold.dim_promotions CASCADE;

CREATE TABLE gold.dim_promotions AS
SELECT
    promo_id,
    promo_name,
    start_date,
    end_date,
    discount_pct,
    scope
FROM silver.promotions;