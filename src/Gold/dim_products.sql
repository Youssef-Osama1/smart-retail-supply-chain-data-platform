DROP TABLE IF EXISTS gold.dim_products CASCADE;

CREATE TABLE gold.dim_products AS
SELECT
    product_id,
    product_name,
    category,
    target_segment,
    fabric,
    style,
    unit_price,
    cost,
    launch_date
FROM silver.products;