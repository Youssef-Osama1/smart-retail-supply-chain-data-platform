{{ config(
    materialized='table',
    indexes=[
        {'columns': ['customer_id']},
        {'columns': ['product_id']},
        {'columns': ['store_id']},
        {'columns': ['date_key']},
        {'columns': ['channel']},
        {'columns': ['promo_id']}
    ]
) }}

SELECT
    oi.order_item_id,
    o.order_id,

    o.customer_id,
    o.store_id::bigint AS store_id,
    oi.product_id,
    o.channel,
    pr.promo_id,                                               -- promotion in effect at order date (NULL if none)

    TO_CHAR(o.order_date::date, 'YYYYMMDD')::int AS date_key,

    oi.quantity,
    oi.unit_price,                                              -- list price
    oi.discount_pct,
    oi.price_paid,                                             -- transaction price

    ROUND((oi.quantity * oi.unit_price)::numeric, 2)              AS gross_amount,
    ROUND((oi.quantity * (oi.unit_price - oi.price_paid))::numeric, 2) AS discount_amount,
    ROUND((oi.quantity * oi.price_paid)::numeric, 2)             AS net_amount,
    ROUND((oi.quantity * p.cost)::numeric, 2)                    AS cost_amount,
    ROUND((oi.quantity * (oi.price_paid - p.cost))::numeric, 2)  AS margin_amount
FROM {{ source('silver', 'order_items') }} oi
JOIN {{ source('silver', 'orders') }} o   ON oi.order_id = o.order_id
JOIN {{ source('silver', 'products') }} p ON oi.product_id = p.product_id


LEFT JOIN LATERAL (
    SELECT pm.promo_id
    FROM {{ source('silver', 'promotions') }} pm
    WHERE o.order_date::date BETWEEN pm.start_date::date AND pm.end_date::date
      AND (pm.scope = 'all' OR p.category = ANY(string_to_array(pm.scope, '|')))
    ORDER BY pm.promo_id
    LIMIT 1
) pr ON TRUE
WHERE o.order_status = 'completed'
