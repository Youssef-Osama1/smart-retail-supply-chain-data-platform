SELECT
    snapshot_date_key,
    location_id,
    location_type,
    product_id,
    COUNT(*) AS n_rows
FROM {{ ref('fact_inventory') }}
GROUP BY 1, 2, 3, 4
HAVING COUNT(*) > 1
