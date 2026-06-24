DROP TABLE IF EXISTS gold.dim_location CASCADE;

-- Unified location dimension so fact_inventory (which mixes store and warehouse
-- snapshots) can hang off ONE relationship in the Power BI model instead of a
-- polymorphic location_id that points at two different dimensions.
-- Surrogate key = location_type || '-' || location_id  (e.g. 'store-1', 'warehouse-2').
CREATE TABLE gold.dim_location AS
SELECT
    'store-' || store_id::text AS location_key,
    store_id                   AS location_id,
    'store'                    AS location_type,
    store_name                 AS location_name,
    city,
    country
FROM gold.dim_stores

UNION ALL

SELECT
    'warehouse-' || warehouse_id::text AS location_key,
    warehouse_id                       AS location_id,
    'warehouse'                        AS location_type,
    warehouse_name                     AS location_name,
    city,
    country
FROM gold.dim_warehouses;
