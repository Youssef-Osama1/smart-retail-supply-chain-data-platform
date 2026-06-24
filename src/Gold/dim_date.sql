DROP TABLE IF EXISTS gold.dim_date CASCADE;

CREATE TABLE gold.dim_date AS
SELECT DISTINCT
    TO_CHAR(d::date, 'YYYYMMDD')::int AS date_key,
    d::date AS full_date,
    EXTRACT(YEAR FROM d) AS year,
    EXTRACT(QUARTER FROM d) AS quarter,
    EXTRACT(MONTH FROM d) AS month,
    TO_CHAR(d::date, 'Month') AS month_name,
    EXTRACT(DAY FROM d) AS day,
    EXTRACT(ISODOW FROM d) AS day_of_week,
    TO_CHAR(d::date, 'Day') AS day_name,
    CASE WHEN EXTRACT(ISODOW FROM d) IN (6, 7) THEN TRUE ELSE FALSE END AS is_weekend
FROM generate_series(
    '2020-01-01'::date,
    '2030-12-31'::date,
    interval '1 day'
) d;