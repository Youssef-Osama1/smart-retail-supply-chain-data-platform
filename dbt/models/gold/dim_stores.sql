{{ config(materialized='table') }}

SELECT
    store_id,
    store_name,
    city,
    country
FROM {{ source('silver', 'stores') }}
