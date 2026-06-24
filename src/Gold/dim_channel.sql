DROP TABLE IF EXISTS gold.dim_channel CASCADE;

CREATE TABLE gold.dim_channel AS
SELECT DISTINCT
    channel AS channel_id,
    INITCAP(REPLACE(channel, '_', ' ')) AS channel_name
FROM silver.orders
WHERE channel IS NOT NULL;