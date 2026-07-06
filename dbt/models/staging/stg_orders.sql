{{ config(materialized='view') }}

SELECT
    order_id,
    customer_id,
    store_id::bigint          AS store_id,
    order_date::timestamp     AS order_date,
    channel,
    order_status,
    'batch'                   AS source_system
FROM {{ source('silver', 'orders') }}

UNION ALL

SELECT
    order_id,
    customer_id,
    store_id,
    order_date::timestamp     AS order_date,
    channel,
    order_status,
    'stream'                  AS source_system
FROM {{ source('bronze_stream', 'orders_raw') }}
