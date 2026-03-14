DROP TABLE IF EXISTS gold.fact_inventory;

CREATE TABLE gold.fact_inventory AS

SELECT
    product_id,
    store_id AS location_id,
    'store' AS location_type,
    quantity_on_hand
FROM silver.store_inventory

UNION ALL

SELECT
    product_id,
    warehouse_id AS location_id,
    'warehouse' AS location_type,
    quantity_on_hand
FROM silver.warehouse_inventory;