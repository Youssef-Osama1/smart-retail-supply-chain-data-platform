{{ config(materialized='table') }}

SELECT
    promo_id,
    promo_name,
    start_date,
    end_date,
    discount_pct,
    scope
FROM {{ source('silver', 'promotions') }}
