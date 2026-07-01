{{ config(
    materialized='table',
    indexes=[
        {'columns': ['ship_date_key']}
    ]
) }}

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
FROM {{ source('silver', 'shipments') }} s
