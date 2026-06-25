-- =====================================================================
-- PRIMARY KEYS
-- =====================================================================

-- Dimensions
ALTER TABLE gold.dim_customers  ADD CONSTRAINT pk_dim_customers  PRIMARY KEY (customer_id);
ALTER TABLE gold.dim_products   ADD CONSTRAINT pk_dim_products   PRIMARY KEY (product_id);
ALTER TABLE gold.dim_stores     ADD CONSTRAINT pk_dim_stores     PRIMARY KEY (store_id);
ALTER TABLE gold.dim_warehouses ADD CONSTRAINT pk_dim_warehouses PRIMARY KEY (warehouse_id);
ALTER TABLE gold.dim_date       ADD CONSTRAINT pk_dim_date       PRIMARY KEY (date_key);
ALTER TABLE gold.dim_channel    ADD CONSTRAINT pk_dim_channel    PRIMARY KEY (channel_id);
ALTER TABLE gold.dim_promotions ADD CONSTRAINT pk_dim_promotions PRIMARY KEY (promo_id);
ALTER TABLE gold.dim_location   ADD CONSTRAINT pk_dim_location   PRIMARY KEY (location_key);

-- Facts
ALTER TABLE gold.fact_sales            ADD CONSTRAINT pk_fact_sales            PRIMARY KEY (order_item_id);
ALTER TABLE gold.fact_shipments        ADD CONSTRAINT pk_fact_shipments        PRIMARY KEY (shipment_item_id);
ALTER TABLE gold.fact_shipment_summary ADD CONSTRAINT pk_fact_shipment_summary PRIMARY KEY (shipment_id);
ALTER TABLE gold.fact_returns          ADD CONSTRAINT pk_fact_returns          PRIMARY KEY (return_id);
ALTER TABLE gold.fact_inventory        ADD CONSTRAINT pk_fact_inventory
    PRIMARY KEY (snapshot_date_key, location_id, location_type, product_id);

-- =====================================================================
-- FOREIGN KEYS
-- =====================================================================

-- fact_sales
ALTER TABLE gold.fact_sales ADD CONSTRAINT fk_sales_customer FOREIGN KEY (customer_id) REFERENCES gold.dim_customers(customer_id);
ALTER TABLE gold.fact_sales ADD CONSTRAINT fk_sales_product  FOREIGN KEY (product_id)  REFERENCES gold.dim_products(product_id);
ALTER TABLE gold.fact_sales ADD CONSTRAINT fk_sales_store    FOREIGN KEY (store_id)    REFERENCES gold.dim_stores(store_id);
ALTER TABLE gold.fact_sales ADD CONSTRAINT fk_sales_date     FOREIGN KEY (date_key)    REFERENCES gold.dim_date(date_key);
ALTER TABLE gold.fact_sales ADD CONSTRAINT fk_sales_channel  FOREIGN KEY (channel)     REFERENCES gold.dim_channel(channel_id);
ALTER TABLE gold.fact_sales ADD CONSTRAINT fk_sales_promo    FOREIGN KEY (promo_id)    REFERENCES gold.dim_promotions(promo_id);

-- fact_shipments (item grain)
ALTER TABLE gold.fact_shipments ADD CONSTRAINT fk_ship_customer  FOREIGN KEY (customer_id)       REFERENCES gold.dim_customers(customer_id);
ALTER TABLE gold.fact_shipments ADD CONSTRAINT fk_ship_product   FOREIGN KEY (product_id)        REFERENCES gold.dim_products(product_id);
ALTER TABLE gold.fact_shipments ADD CONSTRAINT fk_ship_warehouse FOREIGN KEY (warehouse_id)      REFERENCES gold.dim_warehouses(warehouse_id);
ALTER TABLE gold.fact_shipments ADD CONSTRAINT fk_ship_shipdate  FOREIGN KEY (ship_date_key)     REFERENCES gold.dim_date(date_key);
ALTER TABLE gold.fact_shipments ADD CONSTRAINT fk_ship_delivdate FOREIGN KEY (delivery_date_key) REFERENCES gold.dim_date(date_key);

-- fact_shipment_summary (shipment grain)
ALTER TABLE gold.fact_shipment_summary ADD CONSTRAINT fk_shipsum_customer  FOREIGN KEY (customer_id)       REFERENCES gold.dim_customers(customer_id);
ALTER TABLE gold.fact_shipment_summary ADD CONSTRAINT fk_shipsum_warehouse FOREIGN KEY (warehouse_id)      REFERENCES gold.dim_warehouses(warehouse_id);
ALTER TABLE gold.fact_shipment_summary ADD CONSTRAINT fk_shipsum_shipdate  FOREIGN KEY (ship_date_key)     REFERENCES gold.dim_date(date_key);
ALTER TABLE gold.fact_shipment_summary ADD CONSTRAINT fk_shipsum_delivdate FOREIGN KEY (delivery_date_key) REFERENCES gold.dim_date(date_key);

-- fact_returns
ALTER TABLE gold.fact_returns ADD CONSTRAINT fk_ret_customer FOREIGN KEY (customer_id)     REFERENCES gold.dim_customers(customer_id);
ALTER TABLE gold.fact_returns ADD CONSTRAINT fk_ret_product  FOREIGN KEY (product_id)      REFERENCES gold.dim_products(product_id);
ALTER TABLE gold.fact_returns ADD CONSTRAINT fk_ret_date     FOREIGN KEY (return_date_key) REFERENCES gold.dim_date(date_key);
ALTER TABLE gold.fact_returns ADD CONSTRAINT fk_ret_channel  FOREIGN KEY (channel)         REFERENCES gold.dim_channel(channel_id);

-- fact_inventory (store/warehouse unified through gold.dim_location via location_key)
ALTER TABLE gold.fact_inventory ADD CONSTRAINT fk_inv_product  FOREIGN KEY (product_id)        REFERENCES gold.dim_products(product_id);
ALTER TABLE gold.fact_inventory ADD CONSTRAINT fk_inv_date     FOREIGN KEY (snapshot_date_key) REFERENCES gold.dim_date(date_key);
ALTER TABLE gold.fact_inventory ADD CONSTRAINT fk_inv_location FOREIGN KEY (location_key)      REFERENCES gold.dim_location(location_key);

-- =====================================================================
-- INDEXES on foreign-key columns (Postgres does NOT auto-index FKs)
-- =====================================================================

CREATE INDEX IF NOT EXISTS ix_sales_customer ON gold.fact_sales(customer_id);
CREATE INDEX IF NOT EXISTS ix_sales_product  ON gold.fact_sales(product_id);
CREATE INDEX IF NOT EXISTS ix_sales_store    ON gold.fact_sales(store_id);
CREATE INDEX IF NOT EXISTS ix_sales_date     ON gold.fact_sales(date_key);
CREATE INDEX IF NOT EXISTS ix_sales_channel  ON gold.fact_sales(channel);
CREATE INDEX IF NOT EXISTS ix_sales_promo    ON gold.fact_sales(promo_id);

CREATE INDEX IF NOT EXISTS ix_ship_product   ON gold.fact_shipments(product_id);
CREATE INDEX IF NOT EXISTS ix_ship_warehouse ON gold.fact_shipments(warehouse_id);
CREATE INDEX IF NOT EXISTS ix_ship_shipdate  ON gold.fact_shipments(ship_date_key);

CREATE INDEX IF NOT EXISTS ix_shipsum_shipdate ON gold.fact_shipment_summary(ship_date_key);

CREATE INDEX IF NOT EXISTS ix_ret_product ON gold.fact_returns(product_id);
CREATE INDEX IF NOT EXISTS ix_ret_date    ON gold.fact_returns(return_date_key);

CREATE INDEX IF NOT EXISTS ix_inv_product  ON gold.fact_inventory(product_id);
CREATE INDEX IF NOT EXISTS ix_inv_date     ON gold.fact_inventory(snapshot_date_key);
CREATE INDEX IF NOT EXISTS ix_inv_location ON gold.fact_inventory(location_key);