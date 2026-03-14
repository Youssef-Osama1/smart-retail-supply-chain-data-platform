DROP TABLE IF EXISTS gold.dim_products;

CREATE TABLE gold.dim_products AS
SELECT
    product_id,
    product_name,
    category,
    target_segment,
    unit_price
FROM silver.products;