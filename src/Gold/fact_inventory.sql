DROP TABLE IF EXISTS gold.fact_inventory CASCADE;

CREATE TABLE gold.fact_inventory AS

SELECT
    TO_CHAR(snapshot_date::date, 'YYYYMMDD')::int AS snapshot_date_key,
    product_id,
    store_id AS location_id,
    'store' AS location_type,
    'store-' || store_id::text AS location_key,   -- FK into gold.dim_location
    quantity_on_hand,
    units_sold,
    stockout_flag
FROM silver.store_inventory

UNION ALL

SELECT
    TO_CHAR(snapshot_date::date, 'YYYYMMDD')::int AS snapshot_date_key,
    product_id,
    warehouse_id AS location_id,
    'warehouse' AS location_type,
    'warehouse-' || warehouse_id::text AS location_key,   -- FK into gold.dim_location
    quantity_on_hand,
    units_sold,
    stockout_flag
FROM silver.warehouse_inventory;