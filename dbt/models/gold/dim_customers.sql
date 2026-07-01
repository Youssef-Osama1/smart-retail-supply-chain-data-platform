{{ config(materialized='table') }}

SELECT
    customer_id,
    first_name,
    last_name,
    email,
    date_of_birth,
    gender,
    city,
    country,
    signup_date
FROM {{ source('silver', 'customers') }}
