import pandas as pd
import numpy as np
from faker import Faker
import random
from pathlib import Path
from datetime import date, timedelta
from src.config import *


np.random.seed(SEED)
random.seed(SEED)

Faker.seed(SEED)
fake = Faker()

RAW_PATH = Path("data/01_raw_clean")
RAW_PATH.mkdir(parents=True, exist_ok=True)



#----------------------------------------------------------------------------------

cities = []
for country, city_list in COUNTRY_CITY_MAP.items():
    for city in city_list:
        cities.append({
            "country": country,
            "city": city
        })
cities_df = pd.DataFrame(cities)

stores = []
store_id = 1
for _, row in cities_df.iterrows():
    stores.append({
        "store_id": store_id,
        "store_name": f"ZARA Store {store_id}",
        "city": row["city"],
        "country": row["country"]
    })
    store_id += 1

remaining_stores = N_STORES - len(stores)
extra_cities = cities_df.sample(remaining_stores, random_state=42)
for _, row in extra_cities.iterrows():
    stores.append({
        "store_id": store_id,
        "store_name": f"ZARA Store {store_id}",
        "city": row["city"],
        "country": row["country"]
    })
    store_id += 1
df_stores = pd.DataFrame(stores)
df_stores.to_csv(RAW_PATH / "stores.csv", index=False)

#----------------------------------------------------------------------------------

warehouses = []
warehouse_id = 1
for country, city_list in COUNTRY_CITY_MAP.items():
    city = random.choice(city_list)
    warehouses.append({
        "warehouse_id": warehouse_id,
        "warehouse_name": f"ZARA Warehouse {country}",
        "city": city,
        "country": country
    })
    warehouse_id += 1
df_warehouses = pd.DataFrame(warehouses)
df_warehouses.to_csv(RAW_PATH / "warehouses.csv", index=False)


#----------------------------------------------------------------------------------

products = []
product_id = 1

segments = list(SEGMENT_WEIGHTS.keys())
weights = list(SEGMENT_WEIGHTS.values())

used_product_names = set()

while len(products) < N_PRODUCTS:
    segment = random.choices(segments, weights=weights, k=1)[0]

    category = random.choice(ZARA_CATEGORIES[segment])

    style = random.choice(STYLES)
    fabric = random.choice(FABRIC_BY_CATEGORY[category])
    base_name = SINGULAR_MAP[category]

    product_name = f"{style} {fabric} {base_name}"

    if product_name in used_product_names:
        continue

    used_product_names.add(product_name)

    price_min, price_max = PRICE_RANGES[category]
    unit_price = round(np.random.uniform(price_min, price_max), 2)
    unit_price = int(unit_price) + 0.99

    products.append({
        "product_id": product_id,
        "product_name": product_name,
        "target_segment": segment,
        "category": category,
        "unit_price": unit_price
    })
    product_id += 1

df_products = pd.DataFrame(products)
df_products.to_csv(RAW_PATH / "products.csv", index=False)

product_segment_map = dict(
    zip(df_products["product_id"], df_products["target_segment"])
)

product_category_map = dict(
    zip(df_products["product_id"], df_products["category"])
)

products_by_segment = {
    segment: df_products[df_products["target_segment"] == segment]["product_id"].tolist()
    for segment in SEGMENT_WEIGHTS.keys()
}

seasonal_categories = {
    "winter": ["Coats", "Jackets", "Hoodies"],
    "summer": ["Dresses", "T-Shirts", "Skirts"]
}

#----------------------------------------------------------------------------------

customers = []
customer_id = 1

today = date.today()

def generate_birth_date():
    r = random.random()
    if r < 0.7:
        # 18–45
        age = random.randint(18, 45)
    elif r < 0.9:
        # 46–60
        age = random.randint(46, 60)
    else:
        # 16–17
        age = random.randint(16, 17)
    return today - timedelta(days=age * 365)

for _ in range(N_CUSTOMERS):
    country = random.choice(list(COUNTRY_CITY_MAP.keys()))
    city = random.choice(COUNTRY_CITY_MAP[country])
    gender = random.choice(GENDERS)
    if gender == "Male":
        first_name = fake.first_name_male()
    else:
        first_name = fake.first_name_female()

    customers.append({
        "customer_id": customer_id,
        "first_name": first_name,
        "last_name": fake.last_name(),
        "email": fake.unique.email(),
        "date_of_birth": generate_birth_date(),
        "gender": gender,
        "city": city,
        "country": country
    })

    customer_id += 1

df_customers = pd.DataFrame(customers)
df_customers.to_csv(RAW_PATH / "customers.csv", index=False)

# Calculate customer age (for smarter product selection)
def calculate_age(dob):
    return (date.today() - dob).days // 365

df_customers["age"] = df_customers["date_of_birth"].apply(calculate_age)

#----------------------------------------------------------------------------------

orders = []
order_id = 1

channels = list(ORDER_CHANNEL_WEIGHTS.keys())
channel_weights = list(ORDER_CHANNEL_WEIGHTS.values())

store_ids = df_stores["store_id"].tolist()
customer_ids = df_customers["customer_id"].tolist()

def random_order_date(start, end):
    delta_days = (end - start).days
    return start + timedelta(days=random.randint(0, delta_days))

for _ in range(N_ORDERS):
    channel = random.choices(channels, weights=channel_weights, k=1)[0]
    customer_id = random.choice(customer_ids)

    if channel == "in_store":
        store_id = random.choice(store_ids)
    else:
        store_id = None

    orders.append({
        "order_id": order_id,
        "customer_id": customer_id,
        "store_id": store_id,
        "order_date": random_order_date(ORDER_START_DATE, ORDER_END_DATE),
        "channel": channel,
        "total_amount": 0.0
    })

    order_id += 1
df_orders = pd.DataFrame(orders)
df_orders.to_csv(RAW_PATH / "orders.csv", index=False)

#----------------------------------------------------------------------------------


order_items = []
order_item_id = 1

product_price_map = dict(
    zip(df_products["product_id"], df_products["unit_price"])
)

product_ids = df_products["product_id"].tolist()

quantity_values = list(QUANTITY_WEIGHTS.keys())
quantity_weights = list(QUANTITY_WEIGHTS.values())

order_totals = {}

customer_map = df_customers.set_index("customer_id").to_dict("index")

for _, order in df_orders.iterrows():
    order_id = order["order_id"]
    customer_id = order["customer_id"]

    n_items = random.randint(MIN_ITEMS_PER_ORDER, MAX_ITEMS_PER_ORDER)

    customer_row = customer_map[customer_id]
    customer_age = customer_row["age"]
    customer_gender = customer_row["gender"]

    # Segment Filtering
    if customer_age < 18:
        eligible_products = products_by_segment["Kids"]

    elif customer_gender == "Female":
        eligible_products = (
            products_by_segment["Women"] +
            products_by_segment["Accessories"]
        )

    else:
        eligible_products = (
            products_by_segment["Men"] +
            products_by_segment["Accessories"]
        )

    eligible_products = list(set(eligible_products))

    # Seasonality
    order_month = order["order_date"].month

    if order_month in [11, 12, 1, 2]:
        season = "winter"
    elif order_month in [5, 6, 7, 8]:
        season = "summer"
    else:
        season = "normal"

    if season != "normal":
        seasonal_products = [
            pid for pid in eligible_products
            if product_category_map[pid] in seasonal_categories[season]
        ]

        if seasonal_products and random.random() < 0.6:
            pool = seasonal_products
        else:
            pool = eligible_products
    else:
        pool = eligible_products

    if len(pool) >= n_items:
        chosen_products = random.sample(pool, n_items)
    else:
        chosen_products = random.sample(product_ids, n_items)

    total_amount = 0.0

    for product_id in chosen_products:
        quantity = random.choices(
            quantity_values,
            weights=quantity_weights,
            k=1
        )[0]

        unit_price = product_price_map[product_id]
        line_total = quantity * unit_price
        total_amount += line_total

        order_items.append({
            "order_item_id": order_item_id,
            "order_id": order_id,
            "product_id": product_id,
            "quantity": quantity,
            "unit_price": unit_price
        })

        order_item_id += 1

    order_totals[order_id] = round(total_amount, 2)


df_order_items = pd.DataFrame(order_items)
df_order_items.to_csv(RAW_PATH / "order_items.csv", index=False)

df_orders["total_amount"] = df_orders["order_id"].map(order_totals)
df_orders.to_csv(RAW_PATH / "orders.csv", index=False)

#----------------------------------------------------------------------------------


store_inventory = []

product_ids = df_products["product_id"].tolist()
n_products_per_store = int(len(product_ids) * STORE_PRODUCT_COVERAGE)

for _, store in df_stores.iterrows():
    store_id = store["store_id"]

    active_products = random.sample(
        product_ids,
        n_products_per_store
    )

    for product_id in active_products:
        quantity = random.randint(
            STORE_STOCK_RANGE[0],
            STORE_STOCK_RANGE[1]
        )

        store_inventory.append({
            "store_id": store_id,
            "product_id": product_id,
            "quantity_on_hand": quantity
        })

df_store_inventory = pd.DataFrame(store_inventory)

df_store_inventory.to_csv(
    RAW_PATH / "store_inventory.csv",
    index=False
)


#----------------------------------------------------------------------------------


warehouse_inventory = []

for _, warehouse in df_warehouses.iterrows():
    warehouse_id = warehouse["warehouse_id"]

    for _, product in df_products.iterrows():
        quantity = random.randint(
            WAREHOUSE_STOCK_RANGE[0],
            WAREHOUSE_STOCK_RANGE[1]
        )

        warehouse_inventory.append({
            "warehouse_id": warehouse_id,
            "product_id": product["product_id"],
            "quantity_on_hand": quantity
        })

df_warehouse_inventory = pd.DataFrame(warehouse_inventory)
df_warehouse_inventory.to_csv(
    RAW_PATH / "warehouse_inventory.csv",
    index=False
)

#----------------------------------------------------------------------------------

warehouse_country_map = dict(zip(df_warehouses["country"], df_warehouses["warehouse_id"]))
online_orders = df_orders[df_orders["channel"] == "online"]

shipments = []
shipment_id = 1

customer_country_map = dict(
    zip(df_customers["customer_id"], df_customers["country"])
)

for _, order in online_orders.iterrows():
    customer_id = order["customer_id"]
    customer_country = customer_country_map[customer_id]

    warehouse_id = warehouse_country_map[customer_country]
    shipping_delay = random.randint(1, 2)
    delivery_delay = random.randint(2, 7)
    shipping_date = order["order_date"] + timedelta(days=shipping_delay)
    delivery_date = shipping_date + timedelta(days=delivery_delay)
    shipments.append({
        "shipment_id": shipment_id,
        "order_id": order["order_id"],
        "warehouse_id": warehouse_id,
        "customer_id": customer_id,
        "shipping_date": shipping_date,
        "delivery_date": delivery_date,
        "shipping_cost": 0.0
    })
    shipment_id += 1
df_shipments = pd.DataFrame(shipments)
df_shipments.to_csv(RAW_PATH / "shipments.csv", index=False)

#----------------------------------------------------------------------------------

order_items_map = df_order_items.groupby("order_id")

shipment_items = []
shipment_item_id = 1
shipping_costs = {}

for _, shipment in df_shipments.iterrows():
    order_id = shipment["order_id"]
    shipment_id = shipment["shipment_id"]
    total_quantity = 0
    for _, item in order_items_map.get_group(order_id).iterrows():
        quantity = item["quantity"]
        total_quantity += quantity
        shipment_items.append({
            "shipment_item_id": shipment_item_id,
            "shipment_id": shipment_id,
            "product_id": item["product_id"],
            "quantity": quantity
        })
        shipment_item_id += 1
    shipping_costs[shipment_id] = round(
        5 + total_quantity * 2 + np.random.uniform(0, 5),
        2
    )
df_shipment_items = pd.DataFrame(shipment_items)
df_shipment_items.to_csv(RAW_PATH / "shipment_items.csv", index=False)

df_shipments["shipping_cost"] = df_shipments["shipment_id"].map(shipping_costs)
df_shipments.to_csv(RAW_PATH / "shipments.csv", index=False)