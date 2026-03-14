DROP TABLE IF EXISTS gold.dim_date;

CREATE TABLE gold.dim_date AS
SELECT DISTINCT
    TO_CHAR(d::date, 'YYYYMMDD')::int AS date_key,
    d::date AS full_date,
    EXTRACT(YEAR FROM d) AS year,
    EXTRACT(MONTH FROM d) AS month,
    EXTRACT(DAY FROM d) AS day
FROM generate_series(
    (SELECT MIN(order_date::date) FROM silver.orders),
    (SELECT MAX(order_date::date) FROM silver.orders),
    interval '1 day'
) d;