{{ config(materialized='view') }}

SELECT
    order_item_id,
    order_id,
    product_id,
    quantity,
    unit_price,
    discount_pct,
    price_paid,
    line_total,
    'batch'      AS source_system
FROM {{ source('silver', 'order_items') }}

UNION ALL

SELECT
    order_item_id,
    order_id,
    product_id,
    quantity,
    unit_price,
    discount_pct,
    price_paid,
    line_total,
    'stream'     AS source_system
FROM {{ source('bronze_stream', 'order_items_raw') }}
