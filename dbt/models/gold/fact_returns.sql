{{ config(
    materialized='table',
    indexes=[
        {'columns': ['product_id']},
        {'columns': ['return_date_key']}
    ]
) }}

-- Grain: returned order line.
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
FROM {{ source('silver', 'returns') }} r
JOIN {{ source('silver', 'orders') }} o ON r.order_id = o.order_id
