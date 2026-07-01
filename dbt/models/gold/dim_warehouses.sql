{{ config(materialized='table') }}

SELECT
    warehouse_id,
    warehouse_name,
    city,
    country
FROM {{ source('silver', 'warehouses') }}
