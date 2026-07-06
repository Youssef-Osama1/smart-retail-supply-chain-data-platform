{% macro ensure_stream_tables() %}
CREATE SCHEMA IF NOT EXISTS bronze_stream;

CREATE TABLE IF NOT EXISTS bronze_stream.orders_raw (
    event_id        text,
    order_id        bigint,
    customer_id     bigint,
    store_id        bigint,
    order_date      timestamptz,
    channel         text,
    order_status    text,
    total_amount    numeric,
    kafka_partition int,
    kafka_offset    bigint,
    ingested_at     timestamptz DEFAULT now()
);

CREATE TABLE IF NOT EXISTS bronze_stream.order_items_raw (
    event_id       text,
    order_item_id  bigint,
    order_id       bigint,
    product_id     bigint,
    quantity       int,
    unit_price     numeric,
    discount_pct   numeric,
    price_paid     numeric,
    line_total     numeric,
    ingested_at    timestamptz DEFAULT now()
);
{% endmacro %}
