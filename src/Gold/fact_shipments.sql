DROP TABLE IF EXISTS gold.fact_shipments CASCADE;

-- Grain: shipment item. NOTE: shipping_cost and delivery_days are at SHIPMENT
-- grain and repeat across a shipment's item rows. In Power BI aggregate them
-- against gold.fact_shipment_summary (below), not by summing this table, to
-- avoid double counting.
CREATE TABLE gold.fact_shipments AS
SELECT
    si.shipment_item_id,
    s.shipment_id,

    s.order_id,
    s.customer_id,
    s.warehouse_id,
    si.product_id::bigint AS product_id,

    TO_CHAR(s.shipping_date::date, 'YYYYMMDD')::int AS ship_date_key,
    TO_CHAR(s.delivery_date::date, 'YYYYMMDD')::int AS delivery_date_key,

    s.shipping_method,
    s.delivery_status,
    si.quantity,
    s.shipping_cost,
    (s.delivery_date::date - s.shipping_date::date) AS delivery_days
FROM silver.shipment_items si
JOIN silver.shipments s ON si.shipment_id = s.shipment_id;

-- Shipment-grain summary fact for cost / SLA measures (no double counting).
DROP TABLE IF EXISTS gold.fact_shipment_summary CASCADE;

CREATE TABLE gold.fact_shipment_summary AS
SELECT
    s.shipment_id,
    s.order_id,
    s.customer_id,
    s.warehouse_id,
    TO_CHAR(s.shipping_date::date, 'YYYYMMDD')::int AS ship_date_key,
    TO_CHAR(s.delivery_date::date, 'YYYYMMDD')::int AS delivery_date_key,
    s.shipping_method,
    s.delivery_status,
    s.shipping_cost,
    (s.delivery_date::date - s.shipping_date::date) AS delivery_days
FROM silver.shipments s;