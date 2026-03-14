DROP TABLE IF EXISTS gold.dim_warehouses;

CREATE TABLE gold.dim_warehouses AS
SELECT
    warehouse_id,
    warehouse_name,
    city,
    country
FROM silver.warehouses;