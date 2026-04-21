import pandas as pd
import numpy as np
from pathlib import Path
import random
from src.config import *

np.random.seed(SEED)
random.seed(SEED)

CLEAN_PATH = Path("data/01_raw_clean")
DIRTY_PATH = Path("data/02_raw")
DIRTY_PATH.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------------------------------
# Inject Dirty Data - Customers

customers = pd.read_csv(CLEAN_PATH / "customers.csv")

mask = customers.sample(frac=0.05, random_state=1).index
customers.loc[mask, "first_name"] = "  " + customers.loc[mask, "first_name"] + "  "

mask = customers.sample(frac=0.05, random_state=2).index
customers.loc[mask, "last_name"] = customers.loc[mask, "last_name"] + "   "

mask = customers.sample(frac=0.03, random_state=3).index
customers.loc[mask, "first_name"] = customers.loc[mask, "first_name"].str.lower()

mask = customers.sample(frac=0.05, random_state=4).index
customers.loc[mask, "gender"] = np.random.choice(
    ["M", "F", "male", "female"],
    size=len(mask)
)

customers["date_of_birth"] = customers["date_of_birth"].astype(str)

city_typos = {"Madrid": "Madrd", "Rome": "Rom", "Seville": "Sevill"}
for correct, typo in city_typos.items():
    idx = customers[customers["city"] == correct].index
    if len(idx) > 0:
        sample = np.random.choice(idx, size=int(len(idx)*0.3), replace=False)
        customers.loc[sample, "city"] = typo

mask = customers.sample(frac=0.05, random_state=9).index
customers.loc[mask, "country"] = customers.loc[mask, "country"].str.lower()

customers = pd.concat([customers, customers.sample(frac=0.02, random_state=10)])
customers.to_csv(DIRTY_PATH / "customers.csv", index=False)

# --------------------------------------------------------------------------
# Inject Dirty Data - Products

products = pd.read_csv(CLEAN_PATH / "products.csv")

mask = products.sample(frac=0.05, random_state=11).index
products.loc[mask, "product_name"] = "  " + products.loc[mask, "product_name"] + "  "

mask = products.sample(frac=0.03, random_state=12).index
products.loc[mask, "product_name"] = products.loc[mask, "product_name"].str.lower()

mask = products.sample(frac=0.03, random_state=13).index
products.loc[mask, "product_name"] = products.loc[mask, "product_name"].str.replace(" ", "  ")

mask = products.sample(frac=0.05, random_state=14).index
products.loc[mask, "target_segment"] = np.random.choice(
    ["women", "WOMEN", "woman", "men", "kid", "kids"], size=len(mask)
)

category_typos = {"Dresses": "dress", "T-Shirts": "tshirt", "Jeans": "jean", "Shirts": "shirt"}
for correct, typo in category_typos.items():
    idx = products[products["category"] == correct].index
    if len(idx) > 0:
        sample = np.random.choice(idx, size=int(len(idx)*0.25), replace=False)
        products.loc[sample, "category"] = typo

mask = products.sample(frac=0.03, random_state=15).index
products.loc[mask, "category"] = " " + products.loc[mask, "category"] + " "

products["unit_price"] = products["unit_price"].astype(str)

mask = products.sample(frac=0.03, random_state=16).index
products.loc[mask, "unit_price"] = "$" + products.loc[mask, "unit_price"]

mask = products.sample(frac=0.02, random_state=17).index
products.loc[mask, "unit_price"] = products.loc[mask, "unit_price"].str.split(".").str[0]

# FIXED
mask = products.sample(frac=0.01, random_state=18).index
products.loc[mask, "unit_price"] = "-" + products.loc[mask, "unit_price"]

products = pd.concat([products, products.sample(frac=0.02, random_state=19)])
products.to_csv(DIRTY_PATH / "products.csv", index=False)

# --------------------------------------------------------------------------
# Stores

stores = pd.read_csv(CLEAN_PATH / "stores.csv")

mask = stores.sample(frac=0.05, random_state=30).index
stores.loc[mask, "store_name"] = "  " + stores.loc[mask, "store_name"] + "  "

mask = stores.sample(frac=0.03, random_state=31).index
stores.loc[mask, "store_name"] = stores.loc[mask, "store_name"].str.lower()

mask = stores.sample(frac=0.03, random_state=32).index
stores.loc[mask, "store_name"] = stores.loc[mask, "store_name"].str.replace(" ", "  ")

mask = stores.sample(frac=0.03, random_state=33).index
stores.loc[mask, "city"] = " " + stores.loc[mask, "city"] + " "

mask = stores.sample(frac=0.05, random_state=34).index
stores.loc[mask, "country"] = stores.loc[mask, "country"].str.lower()

stores = pd.concat([stores, stores.sample(n=2, random_state=35)], ignore_index=True)
stores.to_csv(DIRTY_PATH / "stores.csv", index=False)

# --------------------------------------------------------------------------
# Warehouses

warehouses = pd.read_csv(CLEAN_PATH / "warehouses.csv")

mask = warehouses.sample(frac=0.05, random_state=40).index
warehouses.loc[mask, "warehouse_name"] = "  " + warehouses.loc[mask, "warehouse_name"] + "  "

mask = warehouses.sample(frac=0.03, random_state=41).index
warehouses.loc[mask, "warehouse_name"] = warehouses.loc[mask, "warehouse_name"].str.lower()

mask = warehouses.sample(frac=0.03, random_state=42).index
warehouses.loc[mask, "warehouse_name"] = warehouses.loc[mask, "warehouse_name"].str.replace(" ", "  ")

mask = warehouses.sample(frac=0.05, random_state=43).index
warehouses.loc[mask, "country"] = warehouses.loc[mask, "country"].str.lower()

warehouses.to_csv(DIRTY_PATH / "warehouses.csv", index=False)

# --------------------------------------------------------------------------
# Store Inventory

store_inventory = pd.read_csv(CLEAN_PATH / "store_inventory.csv")

store_inventory["quantity_on_hand"] = store_inventory["quantity_on_hand"].astype(str)

mask = store_inventory.sample(frac=0.01, random_state=51).index
store_inventory.loc[mask, "quantity_on_hand"] = "-" + store_inventory.loc[mask, "quantity_on_hand"]

store_inventory = pd.concat([store_inventory, store_inventory.sample(frac=0.02, random_state=53)])
store_inventory.to_csv(DIRTY_PATH / "store_inventory.csv", index=False)

# --------------------------------------------------------------------------
# Warehouse Inventory

warehouse_inventory = pd.read_csv(CLEAN_PATH / "warehouse_inventory.csv")

warehouse_inventory["quantity_on_hand"] = warehouse_inventory["quantity_on_hand"].astype(str)

mask = warehouse_inventory.sample(frac=0.01, random_state=61).index
warehouse_inventory.loc[mask, "quantity_on_hand"] = "-" + warehouse_inventory.loc[mask, "quantity_on_hand"]

warehouse_inventory = pd.concat([warehouse_inventory, warehouse_inventory.sample(frac=0.02, random_state=63)])
warehouse_inventory.to_csv(DIRTY_PATH / "warehouse_inventory.csv", index=False)

# --------------------------------------------------------------------------
# Orders

orders = pd.read_csv(CLEAN_PATH / "orders.csv")

orders["order_date"] = orders["order_date"].astype(str)

orders["total_amount"] = orders["total_amount"].astype(str)

mask = orders.sample(frac=0.002, random_state=104).index
orders.loc[mask, "total_amount"] = "-" + orders.loc[mask, "total_amount"]

orders = pd.concat([orders, orders.sample(frac=0.02, random_state=107)])
orders.to_csv(DIRTY_PATH / "orders.csv", index=False)

# --------------------------------------------------------------------------
# Order Items

order_items = pd.read_csv(CLEAN_PATH / "order_items.csv")

order_items["quantity"] = order_items["quantity"].astype(str)

mask = order_items.sample(frac=0.001, random_state=111).index
order_items.loc[mask, "quantity"] = "-" + order_items.loc[mask, "quantity"]

order_items["unit_price"] = order_items["unit_price"].astype(str)

order_items = pd.concat([order_items, order_items.sample(frac=0.02, random_state=114)])
order_items.to_csv(DIRTY_PATH / "order_items.csv", index=False)

# --------------------------------------------------------------------------
# Shipments

shipments = pd.read_csv(CLEAN_PATH / "shipments.csv")

shipments["shipping_cost"] = shipments["shipping_cost"].astype(str)

mask = shipments.sample(frac=0.005, random_state=124).index
shipments.loc[mask, "shipping_cost"] = "-" + shipments.loc[mask, "shipping_cost"]

shipments = pd.concat([shipments, shipments.sample(frac=0.02, random_state=126)])
shipments.to_csv(DIRTY_PATH / "shipments.csv", index=False)

# --------------------------------------------------------------------------
# Shipment Items

shipment_items = pd.read_csv(CLEAN_PATH / "shipment_items.csv")

shipment_items["quantity"] = shipment_items["quantity"].astype(str)

mask = shipment_items.sample(frac=0.005, random_state=131).index
shipment_items.loc[mask, "quantity"] = "-" + shipment_items.loc[mask, "quantity"]

shipment_items = pd.concat([shipment_items, shipment_items.sample(frac=0.02, random_state=135)])
shipment_items.to_csv(DIRTY_PATH / "shipment_items.csv", index=False)