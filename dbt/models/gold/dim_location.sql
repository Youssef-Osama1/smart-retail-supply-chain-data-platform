{{ config(materialized='table') }}

SELECT
    'store-' || store_id::text AS location_key,
    store_id                   AS location_id,
    'store'                    AS location_type,
    store_name                 AS location_name,
    city,
    country
FROM {{ ref('dim_stores') }}

UNION ALL

SELECT
    'warehouse-' || warehouse_id::text AS location_key,
    warehouse_id                       AS location_id,
    'warehouse'                        AS location_type,
    warehouse_name                     AS location_name,
    city,
    country
FROM {{ ref('dim_warehouses') }}
