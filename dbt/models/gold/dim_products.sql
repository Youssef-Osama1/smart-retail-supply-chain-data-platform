{{ config(materialized='table') }}

SELECT
    product_id,
    product_name,
    category,
    target_segment,
    fabric,
    style,
    unit_price,
    cost,
    launch_date
FROM {{ source('silver', 'products') }}
