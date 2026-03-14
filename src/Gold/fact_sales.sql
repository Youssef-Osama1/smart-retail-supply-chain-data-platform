DROP TABLE IF EXISTS gold.fact_sales;

CREATE TABLE gold.fact_sales AS
SELECT
    oi.order_item_id,
    o.order_id,
	
    o.customer_id,
	o.store_id::bigint AS store_id,
	
	TO_CHAR(o.order_date::date,'YYYYMMDD')::int AS date_key,
    
	o.channel,
	
	oi.product_id,
    
    oi.quantity,
    oi.unit_price,
    oi.quantity * oi.unit_price AS sales_amount
	
FROM silver.order_items oi
JOIN silver.orders o
ON oi.order_id = o.order_id;