DROP TABLE IF EXISTS gold.dim_customers;

CREATE TABLE gold.dim_customers AS
SELECT
    customer_id,
    first_name,
    last_name,
	email,
	date_of_birth,
    gender,
    city,
    country
FROM silver.customers;