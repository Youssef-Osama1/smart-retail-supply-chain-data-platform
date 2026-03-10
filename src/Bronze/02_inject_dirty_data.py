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

# Add spaces to first & last names
mask = customers.sample(frac=0.05, random_state=1).index
customers.loc[mask, "first_name"] = "  " + customers.loc[mask, "first_name"] + "  "
mask = customers.sample(frac=0.05, random_state=2).index
customers.loc[mask, "last_name"] = customers.loc[mask, "last_name"] + "   "

# lowercase some names
mask = customers.sample(frac=0.03, random_state=3).index
customers.loc[mask, "first_name"] = customers.loc[mask, "first_name"].str.lower()

# Messy gender
mask = customers.sample(frac=0.05, random_state=4).index
customers.loc[mask, "gender"] = np.random.choice(
    ["M", "F", "male", "female"], 
    size=len(mask)
)

# Convert to string only (no format change)
customers["date_of_birth"] = customers["date_of_birth"].astype(str)

# City issues - Inject typos on sample only
city_typos = {
    "Madrid": "Madrd",
    "Rome": "Rom",
    "Seville": "Sevill"
}
for correct_city, typo_city in city_typos.items():
    city_mask = customers[customers["city"] == correct_city].index
    if len(city_mask) > 0:
        sample_size = int(len(city_mask) * 0.3)
        sampled_indices = np.random.choice(
            city_mask, 
            size=sample_size, 
            replace=False
        )
        customers.loc[sampled_indices, "city"] = typo_city

# Country lowercase
mask = customers.sample(frac=0.05, random_state=9).index
customers.loc[mask, "country"] = customers.loc[mask, "country"].str.lower()

# Duplicate rows
customers = pd.concat([
    customers,
    customers.sample(frac=0.02, random_state=10)
])

customers.to_csv(DIRTY_PATH / "customers.csv", index=False)

# --------------------------------------------------------------------------

# Inject Dirty Data - Products

products = pd.read_csv(CLEAN_PATH / "products.csv")

# Product name spacing issues
mask = products.sample(frac=0.05, random_state=11).index
products.loc[mask, "product_name"] = "  " + products.loc[mask, "product_name"] + "  "

# lowercase product names
mask = products.sample(frac=0.03, random_state=12).index
products.loc[mask, "product_name"] = products.loc[mask, "product_name"].str.lower()

# double spaces
mask = products.sample(frac=0.03, random_state=13).index
products.loc[mask, "product_name"] = products.loc[mask, "product_name"].str.replace(" ", "  ")

# Dirty target segment
mask = products.sample(frac=0.05, random_state=14).index
products.loc[mask, "target_segment"] = np.random.choice(
    ["women", "WOMEN", "woman", "men", "kid", "kids"],
    size=len(mask)
)

# Category typos
category_typos = {
    "Dresses": "dress",
    "T-Shirts": "tshirt",
    "Jeans": "jean",
    "Shirts": "shirt"
}

for correct, typo in category_typos.items():
    cat_mask = products[products["category"] == correct].index
    if len(cat_mask) > 0:
        sample_size = int(len(cat_mask) * 0.25)
        sampled_indices = np.random.choice(cat_mask, size=sample_size, replace=False)
        products.loc[sampled_indices, "category"] = typo

# Category spacing issues
mask = products.sample(frac=0.03, random_state=15).index
products.loc[mask, "category"] = " " + products.loc[mask, "category"] + " "

# Price formatting issues
products["unit_price"] = products["unit_price"].astype(str)
mask = products.sample(frac=0.03, random_state=16).index
products.loc[mask, "unit_price"] = "$" + products.loc[mask, "unit_price"]

# price as integer string
mask = products.sample(frac=0.02, random_state=17).index
products.loc[mask, "unit_price"] = products.loc[mask, "unit_price"].astype(str).str.split(".").str[0]

# Negative prices (rare)
mask = products.sample(frac=0.01, random_state=18).index
products.loc[mask, "unit_price"] = -products.loc[mask, "unit_price"].astype(float)

# Duplicate rows
products = pd.concat([
    products,
    products.sample(frac=0.02, random_state=19)
])

products.to_csv(DIRTY_PATH / "products.csv", index=False)

# --------------------------------------------------------------------------

# Inject Dirty Data - Stores

stores = pd.read_csv(CLEAN_PATH / "stores.csv")

# store_name spacing
mask = stores.sample(frac=0.05, random_state=30).index
stores.loc[mask, "store_name"] = "  " + stores.loc[mask, "store_name"] + "  "

# lowercase store names
mask = stores.sample(frac=0.03, random_state=31).index
stores.loc[mask, "store_name"] = stores.loc[mask, "store_name"].str.lower()

# double spaces
mask = stores.sample(frac=0.03, random_state=32).index
stores.loc[mask, "store_name"] = stores.loc[mask, "store_name"].str.replace(" ", "  ")

# city typos
city_typos = {
    "Madrid": "Madrd",
    "Seville": "Sevill",
    "Barcelona": "Barcelna"
}

for correct, typo in city_typos.items():
    city_mask = stores[stores["city"] == correct].index
    if len(city_mask) > 0:
        sample_size = int(len(city_mask) * 0.3)
        sampled = np.random.choice(city_mask, size=sample_size, replace=False)
        stores.loc[sampled, "city"] = typo

# city spacing
mask = stores.sample(frac=0.03, random_state=33).index
stores.loc[mask, "city"] = " " + stores.loc[mask, "city"] + " "

# country casing
mask = stores.sample(frac=0.05, random_state=34).index
stores.loc[mask, "country"] = stores.loc[mask, "country"].str.lower()

# duplicates
dup_rows = stores.sample(n=2, random_state=35)
stores = pd.concat([stores, dup_rows], ignore_index=True)

stores.to_csv(DIRTY_PATH / "stores.csv", index=False)

# --------------------------------------------------------------------------

# Inject Dirty Data - Warehouses

warehouses = pd.read_csv(CLEAN_PATH / "warehouses.csv")

# warehouse_name spacing
mask = warehouses.sample(frac=0.05, random_state=40).index
warehouses.loc[mask, "warehouse_name"] = "  " + warehouses.loc[mask, "warehouse_name"] + "  "

# lowercase warehouse names
mask = warehouses.sample(frac=0.03, random_state=41).index
warehouses.loc[mask, "warehouse_name"] = warehouses.loc[mask, "warehouse_name"].str.lower()

# double spaces
mask = warehouses.sample(frac=0.03, random_state=42).index
warehouses.loc[mask, "warehouse_name"] = warehouses.loc[mask, "warehouse_name"].str.replace(" ", "  ")

# city typos
city_typos = {
    "Madrid": "Madrd",
    "Milan": "Miln",
    "Birmingham": "Birminghm"
}

for correct, typo in city_typos.items():
    city_mask = warehouses[warehouses["city"] == correct].index
    if len(city_mask) > 0:
        sample_size = int(len(city_mask) * 0.3)
        sampled = np.random.choice(city_mask, size=sample_size, replace=False)
        warehouses.loc[sampled, "city"] = typo

# country casing
mask = warehouses.sample(frac=0.05, random_state=43).index
warehouses.loc[mask, "country"] = warehouses.loc[mask, "country"].str.lower()

warehouses.to_csv(DIRTY_PATH / "warehouses.csv", index=False)

# --------------------------------------------------------------------------

# Inject Dirty Data - Store Inventory

store_inventory = pd.read_csv(CLEAN_PATH / "store_inventory.csv")

# quantity as string
store_inventory["quantity_on_hand"] = store_inventory["quantity_on_hand"].astype(object)
mask = store_inventory.sample(frac=0.03, random_state=50).index
store_inventory.loc[mask, "quantity_on_hand"] = store_inventory.loc[mask, "quantity_on_hand"].astype(str)

# negative stock
mask = store_inventory.sample(frac=0.01, random_state=51).index
store_inventory.loc[mask, "quantity_on_hand"] = -store_inventory.loc[mask, "quantity_on_hand"].astype(int)

# zero stock
mask = store_inventory.sample(frac=0.02, random_state=52).index
store_inventory.loc[mask, "quantity_on_hand"] = 0

# duplicate rows
store_inventory = pd.concat([
    store_inventory,
    store_inventory.sample(frac=0.02, random_state=53)
])
store_inventory.to_csv(DIRTY_PATH / "store_inventory.csv", index=False)

# --------------------------------------------------------------------------

# Inject Dirty Data - Warehouse Inventory

warehouse_inventory = pd.read_csv(CLEAN_PATH / "warehouse_inventory.csv")

# quantity as string
warehouse_inventory["quantity_on_hand"] = warehouse_inventory["quantity_on_hand"].astype(object)
mask = warehouse_inventory.sample(frac=0.03, random_state=60).index
warehouse_inventory.loc[mask, "quantity_on_hand"] = warehouse_inventory.loc[mask, "quantity_on_hand"].astype(str)

# negative stock
mask = warehouse_inventory.sample(frac=0.01, random_state=61).index
warehouse_inventory.loc[mask, "quantity_on_hand"] = -warehouse_inventory.loc[mask, "quantity_on_hand"].astype(int)

# very large stock (system bug)
mask = warehouse_inventory.sample(frac=0.01, random_state=62).index
warehouse_inventory.loc[mask, "quantity_on_hand"] = 999999

# duplicate rows
warehouse_inventory = pd.concat([
    warehouse_inventory,
    warehouse_inventory.sample(frac=0.02, random_state=63)
])
warehouse_inventory.to_csv(DIRTY_PATH / "warehouse_inventory.csv", index=False)

# --------------------------------------------------------------------------

# Inject Dirty Data - Orders

orders = pd.read_csv(CLEAN_PATH / "orders.csv")

# order_date as string    
orders["order_date"] = orders["order_date"].astype(str)

# mixed date formats
mask = orders.sample(frac=0.03, random_state=100).index
orders.loc[mask, "order_date"] = pd.to_datetime(
    orders.loc[mask, "order_date"]
).dt.strftime("%d/%m/%Y")

# future dates
mask = orders.sample(frac=0.0002, random_state=101).index
orders.loc[mask, "order_date"] = "2035-01-01"

# channel casing inconsistency
mask = orders.sample(frac=0.05, random_state=102).index
orders.loc[mask, "channel"] = (
    orders.loc[mask, "channel"]
    .str.upper()
    .str.replace("_", " ")
)

# total_amount formatting issues
orders["total_amount"] = orders["total_amount"].astype(str)

# negative totals
mask = orders.sample(frac=0.002, random_state=104).index
orders.loc[mask, "total_amount"] = -orders.loc[mask, "total_amount"].astype(float)

# add $
mask = orders.sample(frac=0.002, random_state=103).index
orders.loc[mask, "total_amount"] = "$" + orders.loc[mask, "total_amount"].astype(str)

# inconsistent totals
mask = orders.sample(frac=0.02, random_state=105).index
orders.loc[mask, "total_amount"] = "99999"

# break channel-store logic
# online orders having store_id
store_ids = orders["store_id"].dropna().unique().tolist()
online_mask = orders["channel"] == "ONLINE"
mask = orders[online_mask].sample(frac=0.02, random_state=106).index
orders.loc[mask, "store_id"] = random.choices(store_ids, k=len(mask))

# duplicate rows
orders = pd.concat([
    orders,
    orders.sample(frac=0.02, random_state=107)
])

orders.to_csv(DIRTY_PATH / "orders.csv", index=False)

# --------------------------------------------------------------------------

# Inject Dirty Data - Order Items

order_items = pd.read_csv(CLEAN_PATH / "order_items.csv")

# quantity as string
order_items["quantity"] = order_items["quantity"].astype(str)
mask = order_items.sample(frac=0.03, random_state=110).index
order_items.loc[mask, "quantity"] = order_items.loc[mask, "quantity"]

# negative quantity
mask = order_items.sample(frac=0.001, random_state=111).index
order_items.loc[mask, "quantity"] = -order_items.loc[mask, "quantity"].astype(int)

# unit_price as string with $
order_items["unit_price"] = order_items["unit_price"].astype(str)
mask = order_items.sample(frac=0.03, random_state=112).index
order_items.loc[mask, "unit_price"] = "$" + order_items.loc[mask, "unit_price"]

# wrong price (bug)
mask = order_items.sample(frac=0.01, random_state=113).index
order_items.loc[mask, "unit_price"] = 0.99

# duplicate order items
order_items = pd.concat([
    order_items,
    order_items.sample(frac=0.02, random_state=114)
])

# orphan order_items (order_id not exists)
mask = order_items.sample(frac=0.0005, random_state=115).index
order_items.loc[mask, "order_id"] = 9999999

order_items.to_csv(DIRTY_PATH / "order_items.csv", index=False)

# --------------------------------------------------------------------------

# Inject Dirty Data - shipments

shipments = pd.read_csv(CLEAN_PATH / "shipments.csv")

# shipping_date as string
shipments["shipping_date"] = shipments["shipping_date"].astype(str)

# mixed date formats
mask = shipments.sample(frac=0.03, random_state=120).index
shipments.loc[mask, "shipping_date"] = pd.to_datetime(
    shipments.loc[mask, "shipping_date"]
).dt.strftime("%d/%m/%Y")

# delivery_date mixed formats
shipments["delivery_date"] = shipments["delivery_date"].astype(str)

mask = shipments.sample(frac=0.03, random_state=121).index
shipments.loc[mask, "delivery_date"] = pd.to_datetime(
    shipments.loc[mask, "delivery_date"]
).dt.strftime("%d-%m-%Y")

# delivery before shipping (system bug)
mask = shipments.sample(frac=0.01, random_state=122).index
temp = shipments.loc[mask, "shipping_date"]
shipments.loc[mask, "shipping_date"] = shipments.loc[mask, "delivery_date"]
shipments.loc[mask, "delivery_date"] = temp

# negative shipping cost
mask = shipments.sample(frac=0.005, random_state=124).index
shipments.loc[mask, "shipping_cost"] = -shipments.loc[mask, "shipping_cost"].astype(float)

# shipping_cost formatting issues
shipments["shipping_cost"] = shipments["shipping_cost"].astype(str)
mask = shipments.sample(frac=0.03, random_state=123).index
shipments.loc[mask, "shipping_cost"] = "$" + shipments.loc[mask, "shipping_cost"]

# unrealistic high shipping cost
mask = shipments.sample(frac=0.01, random_state=125).index
shipments.loc[mask, "shipping_cost"] = "1500"

# duplicates
shipments = pd.concat([
    shipments,
    shipments.sample(frac=0.02, random_state=126)
])

shipments.to_csv(DIRTY_PATH / "shipments.csv", index=False)

# --------------------------------------------------------------------------

# Inject Dirty Data - shipment_items

shipment_items = pd.read_csv(CLEAN_PATH / "shipment_items.csv")

# quantity as string
shipment_items["quantity"] = shipment_items["quantity"].astype(str)

# negative quantity
mask = shipment_items.sample(frac=0.005, random_state=131).index
shipment_items.loc[mask, "quantity"] = -shipment_items.loc[mask, "quantity"].astype(float)

# unrealistic quantity (system bug)
mask = shipment_items.sample(frac=0.01, random_state=132).index
shipment_items.loc[mask, "quantity"] = 999

# wrong product_id
mask = shipment_items.sample(frac=0.005, random_state=133).index
shipment_items.loc[mask, "product_id"] = 999999

# orphan shipment_id (shipment not exists)
mask = shipment_items.sample(frac=0.003, random_state=134).index
shipment_items.loc[mask, "shipment_id"] = 8888888

# duplicate rows
shipment_items = pd.concat([
    shipment_items,
    shipment_items.sample(frac=0.02, random_state=135)
])

shipment_items.to_csv(DIRTY_PATH / "shipment_items.csv", index=False)