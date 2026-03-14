DROP TABLE IF EXISTS gold.dim_stores;

CREATE TABLE gold.dim_stores AS
SELECT
    store_id,
    store_name,
    city,
    country
FROM silver.stores;