DROP TABLE IF EXISTS gold.fact_returns CASCADE;

-- Grain: returned order line.
CREATE TABLE gold.fact_returns AS
SELECT
    r.return_id,
    r.order_id,
    r.order_item_id,
    r.product_id,
    o.customer_id,
    o.channel,

    TO_CHAR(r.return_date::date, 'YYYYMMDD')::int AS return_date_key,

    r.quantity_returned,
    r.refund_amount,
    r.reason
FROM silver.returns r
JOIN silver.orders o ON r.order_id = o.order_id;