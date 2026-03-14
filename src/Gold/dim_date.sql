DROP TABLE IF EXISTS gold.dim_date;

CREATE TABLE gold.dim_date AS
SELECT DISTINCT
    TO_CHAR(d::date, 'YYYYMMDD')::int AS date_key,
    d::date AS full_date,
    EXTRACT(YEAR FROM d) AS year,
    EXTRACT(MONTH FROM d) AS month,
    EXTRACT(DAY FROM d) AS day
FROM generate_series(
    '2020-01-01'::date,
    '2030-12-31'::date,
    interval '1 day'
) d;