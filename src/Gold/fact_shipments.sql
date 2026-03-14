DROP TABLE IF EXISTS gold.fact_shipments;

CREATE TABLE gold.fact_shipments AS
SELECT
    si.shipment_item_id,
    s.shipment_id,
	
    s.order_id,
    s.customer_id,
    s.warehouse_id,

	TO_CHAR(s.shipping_date::date,'YYYYMMDD')::int AS ship_date_key,
    TO_CHAR(s.delivery_date::date,'YYYYMMDD')::int AS delivery_date_key,
	
    si.product_id::bigint AS product_id,
    si.quantity,
    
    s.shipping_cost,
	
   	(s.delivery_date::date - s.shipping_date::date) AS delivery_days
	
FROM silver.shipment_items si
JOIN silver.shipments s
ON si.shipment_id = s.shipment_id;