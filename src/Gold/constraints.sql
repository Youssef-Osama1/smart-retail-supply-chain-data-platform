-- PRIMARY KEYS

-- dim tables

ALTER TABLE gold.dim_customers
ADD CONSTRAINT pk_dim_customers
PRIMARY KEY (customer_id);

ALTER TABLE gold.dim_products
ADD CONSTRAINT pk_dim_products
PRIMARY KEY (product_id);

ALTER TABLE gold.dim_stores
ADD CONSTRAINT pk_dim_stores
PRIMARY KEY (store_id);

ALTER TABLE gold.dim_warehouses
ADD CONSTRAINT pk_dim_warehouses
PRIMARY KEY (warehouse_id);

ALTER TABLE gold.dim_date
ADD CONSTRAINT pk_dim_date
PRIMARY KEY (date_key);

/* fact tables */

ALTER TABLE gold.fact_sales
ADD CONSTRAINT pk_fact_sales
PRIMARY KEY (order_item_id);

ALTER TABLE gold.fact_shipments
ADD CONSTRAINT pk_fact_shipments
PRIMARY KEY (shipment_item_id);

-- FOREIGN KEYS

-- fact_sales relationships

ALTER TABLE gold.fact_sales
ADD CONSTRAINT fk_sales_customer
FOREIGN KEY (customer_id)
REFERENCES gold.dim_customers(customer_id);

ALTER TABLE gold.fact_sales
ADD CONSTRAINT fk_sales_product
FOREIGN KEY (product_id)
REFERENCES gold.dim_products(product_id);

ALTER TABLE gold.fact_sales
ADD CONSTRAINT fk_sales_store
FOREIGN KEY (store_id)
REFERENCES gold.dim_stores(store_id);

ALTER TABLE gold.fact_sales
ADD CONSTRAINT fk_sales_date
FOREIGN KEY (date_key)
REFERENCES gold.dim_date(date_key);


/* fact_shipments relationships */

ALTER TABLE gold.fact_shipments
ADD CONSTRAINT fk_shipments_customer
FOREIGN KEY (customer_id)
REFERENCES gold.dim_customers(customer_id);

ALTER TABLE gold.fact_shipments
ADD CONSTRAINT fk_shipments_product
FOREIGN KEY (product_id)
REFERENCES gold.dim_products(product_id);

ALTER TABLE gold.fact_shipments
ADD CONSTRAINT fk_shipments_warehouse
FOREIGN KEY (warehouse_id)
REFERENCES gold.dim_warehouses(warehouse_id);

ALTER TABLE gold.fact_shipments
ADD CONSTRAINT fk_shipments_ship_date
FOREIGN KEY (ship_date_key)
REFERENCES gold.dim_date(date_key);

ALTER TABLE gold.fact_shipments
ADD CONSTRAINT fk_shipments_delivery_date
FOREIGN KEY (delivery_date_key)
REFERENCES gold.dim_date(date_key);

/* fact_inventory relationships */

ALTER TABLE gold.fact_inventory
ADD CONSTRAINT fk_inventory_product
FOREIGN KEY (product_id)
REFERENCES gold.dim_products(product_id);