{{ config(materialized='table') }}

SELECT DISTINCT
    channel AS channel_id,
    INITCAP(REPLACE(channel, '_', ' ')) AS channel_name
FROM {{ source('silver', 'orders') }}
WHERE channel IS NOT NULL
