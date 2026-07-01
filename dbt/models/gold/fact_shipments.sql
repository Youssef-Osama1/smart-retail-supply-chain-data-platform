{{ config(
    materialized='table',
    indexes=[
        {'columns': ['product_id']},
        {'columns': ['warehouse_id']},
        {'columns': ['ship_date_key']}
    ]
) }}


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
FROM {{ source('silver', 'shipment_items') }} si
JOIN {{ source('silver', 'shipments') }} s ON si.shipment_id = s.shipment_id
