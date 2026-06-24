import pandas as pd
import numpy as np
import random
from pathlib import Path
from datetime import date, timedelta
from faker import Faker
from src.config import *

rng = np.random.default_rng(SEED)
random.seed(SEED)
np.random.seed(SEED)
Faker.seed(SEED)
fake = Faker()

RAW_PATH = Path("data/01_raw_clean")
RAW_PATH.mkdir(parents=True, exist_ok=True)


def round2(x):
    return np.round(x, 2)


# --- Stores -----------------------------------------------------------------

cities = [
    {"country": country, "city": city}
    for country, city_list in COUNTRY_CITY_MAP.items()
    for city in city_list
]
cities_df = pd.DataFrame(cities)

# One store per city first, then fill the remainder by sampling cities.
store_rows = cities_df.copy()
remaining = N_STORES - len(store_rows)
if remaining > 0:
    store_rows = pd.concat(
        [store_rows, cities_df.sample(remaining, replace=True, random_state=SEED)],
        ignore_index=True,
    )
store_rows = store_rows.head(N_STORES).reset_index(drop=True)

df_stores = pd.DataFrame({
    "store_id": range(1, len(store_rows) + 1),
    "store_name": [f"ZARA Store {i}" for i in range(1, len(store_rows) + 1)],
    "city": store_rows["city"],
    "country": store_rows["country"],
})
df_stores.to_csv(RAW_PATH / "stores.csv", index=False)

# --- Warehouses (one per country) -------------------------------------------

warehouses = []
for wid, (country, city_list) in enumerate(COUNTRY_CITY_MAP.items(), start=1):
    warehouses.append({
        "warehouse_id": wid,
        "warehouse_name": f"ZARA Warehouse {country}",
        "city": random.choice(city_list),
        "country": country,
    })
df_warehouses = pd.DataFrame(warehouses)
df_warehouses.to_csv(RAW_PATH / "warehouses.csv", index=False)
warehouse_by_country = dict(zip(df_warehouses["country"], df_warehouses["warehouse_id"]))
all_warehouse_ids = df_warehouses["warehouse_id"].tolist()

# --- Products ---------------------------------------------------------------

segments = list(SEGMENT_WEIGHTS.keys())
segment_weights = list(SEGMENT_WEIGHTS.values())

products = []
used_names = set()
product_id = 1
while len(products) < N_PRODUCTS:
    segment = random.choices(segments, weights=segment_weights, k=1)[0]
    category = random.choice(ZARA_CATEGORIES[segment])
    style = random.choice(STYLES)
    fabric = random.choice(FABRIC_BY_CATEGORY[category])
    name = f"{style} {fabric} {SINGULAR_MAP[category]}"
    if name in used_names:
        continue
    used_names.add(name)

    lo, hi = PRICE_RANGES[category]
    unit_price = int(np.random.uniform(lo, hi)) + 0.99
    cost = round2(unit_price * np.random.uniform(*COGS_RATIO_RANGE))

    if random.random() < 0.75:
        launch = ORDER_START_DATE - timedelta(days=random.randint(30, 720))
    else:
        span = (ORDER_END_DATE - ORDER_START_DATE).days
        launch = ORDER_START_DATE + timedelta(days=random.randint(0, span))

    products.append({
        "product_id": product_id,
        "product_name": name,
        "target_segment": segment,
        "category": category,
        "fabric": fabric,
        "style": style,
        "unit_price": unit_price,
        "cost": cost,
        "launch_date": launch,
    })
    product_id += 1

df_products = pd.DataFrame(products)
df_products.to_csv(RAW_PATH / "products.csv", index=False)

product_price_map = dict(zip(df_products["product_id"], df_products["unit_price"]))
product_category_map = dict(zip(df_products["product_id"], df_products["category"]))
products_by_segment = {
    seg: df_products[df_products["target_segment"] == seg]["product_id"].tolist()
    for seg in segments
}
product_ids = df_products["product_id"].tolist()

# --- Customers --------------------------------------------------------------

age_bands = list(AGE_BANDS.keys())
age_band_weights = list(AGE_BANDS.values())


def random_dob():
    band = random.choices(age_bands, weights=age_band_weights, k=1)[0]
    age = random.randint(band[0], band[1])
    day_offset = random.randint(0, 364)
    return REFERENCE_DATE.replace(year=REFERENCE_DATE.year - age) - timedelta(days=day_offset)


customers = []
for cid in range(1, N_CUSTOMERS + 1):
    country = random.choice(list(COUNTRY_CITY_MAP.keys()))
    city = random.choice(COUNTRY_CITY_MAP[country])
    gender = random.choices(list(GENDER_WEIGHTS), weights=list(GENDER_WEIGHTS.values()), k=1)[0]
    first_name = fake.first_name_male() if gender == "Male" else fake.first_name_female()
    customers.append({
        "customer_id": cid,
        "first_name": first_name,
        "last_name": fake.last_name(),
        "email": fake.unique.email(),
        "date_of_birth": random_dob(),
        "gender": gender,
        "city": city,
        "country": country,
    })

df_customers = pd.DataFrame(customers)
df_customers["age"] = df_customers["date_of_birth"].apply(
    lambda d: REFERENCE_DATE.year - d.year - ((REFERENCE_DATE.month, REFERENCE_DATE.day) < (d.month, d.day))
)
customer_ids = df_customers["customer_id"].to_numpy()
customer_info = df_customers.set_index("customer_id")[["age", "gender", "country", "city"]].to_dict("index")

activity_weight = rng.lognormal(mean=0.0, sigma=1.1, size=N_CUSTOMERS)  # heavy-tailed: few customers drive most orders
activity_weight = activity_weight / activity_weight.sum()

# --- Demand model -----------------------------------------------------------

all_days = pd.date_range(ORDER_START_DATE, ORDER_END_DATE, freq="D")


def promo_for(d):
    for promo in PROMOTIONS:
        start = date(d.year, *promo["start"])
        end = date(d.year, *promo["end"])
        if start <= d.date() <= end:
            return promo
    return None


def daily_expected_orders(d):
    years_in = (d.year - ORDER_START_DATE.year) + (d.dayofyear - 1) / 365.0
    trend = (1 + YEARLY_GROWTH) ** years_in
    factor = (
        BASE_DAILY_ORDERS
        * trend
        * WEEKDAY_FACTORS[d.weekday()]
        * MONTH_FACTORS[d.month]
    )
    promo = promo_for(d)
    if promo:
        factor *= promo["demand_multiplier"]
    return factor


expected = np.array([daily_expected_orders(d) for d in all_days])
order_counts = rng.poisson(expected)
order_dates = np.repeat(all_days.values, order_counts)
n_orders = min(len(order_dates), MAX_ORDERS)
order_dates = order_dates[:n_orders]

# Assign customers by activity weight (heavy tail) and channel by weight.
order_customer = rng.choice(customer_ids, size=n_orders, p=activity_weight)
channels = list(ORDER_CHANNEL_WEIGHTS.keys())
channel_p = list(ORDER_CHANNEL_WEIGHTS.values())
order_channel = rng.choice(channels, size=n_orders, p=channel_p)

orders_df = pd.DataFrame({
    "order_id": np.arange(1, n_orders + 1),
    "customer_id": order_customer,
    "order_date": pd.to_datetime(order_dates),
    "channel": order_channel,
}).sort_values("order_date").reset_index(drop=True)
orders_df["order_id"] = np.arange(1, n_orders + 1)

first_order = orders_df.groupby("customer_id")["order_date"].min()
df_customers["signup_date"] = df_customers["customer_id"].map(first_order)
no_order = df_customers["signup_date"].isna()
n_missing = int(no_order.sum())
if n_missing:
    span = (ORDER_END_DATE - ORDER_START_DATE).days
    legacy = rng.random(n_missing) < LEGACY_CUSTOMER_FRACTION
    offsets = np.where(
        legacy,
        -rng.integers(1, 900, n_missing),       # before the window
        rng.integers(0, span + 1, n_missing),   # within the window
    )
    df_customers.loc[no_order, "signup_date"] = [
        pd.Timestamp(ORDER_START_DATE) + pd.Timedelta(days=int(o)) for o in offsets
    ]
df_customers["signup_date"] = df_customers["signup_date"].dt.date
df_customers = df_customers.drop(columns=["age"])
df_customers.to_csv(RAW_PATH / "customers.csv", index=False)

# --- Store stock coverage ---------------------------------------------------

n_per_store = int(len(product_ids) * STORE_PRODUCT_COVERAGE)
store_products = {
    int(sid): set(random.sample(product_ids, n_per_store))
    for sid in df_stores["store_id"]
}
stores_by_city = df_stores.groupby("city")["store_id"].apply(list).to_dict()
stores_by_country = df_stores.groupby("country")["store_id"].apply(list).to_dict()


def pick_store(country, city):
    if city in stores_by_city:
        return random.choice(stores_by_city[city])
    return random.choice(stores_by_country[country])


# --- Order items ------------------------------------------------------------

quantity_values = list(QUANTITY_WEIGHTS.keys())
quantity_p = list(QUANTITY_WEIGHTS.values())


def eligible_pools(age, gender):
    if age < 18:
        return products_by_segment["Kids"], products_by_segment["Accessories"]
    if gender == "Female":
        return (
            products_by_segment["Women"],
            products_by_segment["Accessories"] + products_by_segment["Men"],
        )
    return (
        products_by_segment["Men"],
        products_by_segment["Accessories"] + products_by_segment["Women"],
    )


def season_of(month):
    if month in (11, 12, 1, 2):
        return "winter"
    if month in (5, 6, 7, 8):
        return "summer"
    return "normal"


order_items = []
order_item_id = 1
order_store = {}
order_total = {}

for row in orders_df.itertuples(index=False):
    oid = row.order_id
    cust = customer_info[row.customer_id]
    order_dt = row.order_date

    if row.channel == "in_store":
        store_id = pick_store(cust["country"], cust["city"])
        order_store[oid] = store_id
        stocked = store_products[store_id]
    else:
        order_store[oid] = None
        stocked = None

    primary, secondary = eligible_pools(cust["age"], cust["gender"])
    season = season_of(order_dt.month)
    promo = promo_for(order_dt)

    n_items = random.randint(MIN_ITEMS_PER_ORDER, MAX_ITEMS_PER_ORDER)
    chosen = set()
    attempts = 0
    while len(chosen) < n_items and attempts < n_items * 6:
        attempts += 1
        pool = primary if random.random() < IN_SEGMENT_PROB else secondary
        if not pool:
            pool = product_ids
        pid = random.choice(pool)
        if stocked is not None and pid not in stocked:
            continue
        if season != "normal" and random.random() < SEASONAL_BIAS:
            if product_category_map[pid] not in SEASONAL_CATEGORIES[season]:
                continue
        chosen.add(pid)

    total = 0.0
    for pid in chosen:
        qty = random.choices(quantity_values, weights=quantity_p, k=1)[0]
        list_price = product_price_map[pid]
        discount = 0.0
        if promo and (promo["scope"] == "all" or product_category_map[pid] in promo["scope"]):
            discount = promo["discount_pct"]
        price_paid = round2(list_price * (1 - discount))
        line_total = round2(qty * price_paid)
        total += line_total
        order_items.append({
            "order_item_id": order_item_id,
            "order_id": oid,
            "product_id": pid,
            "quantity": qty,
            "unit_price": list_price,
            "discount_pct": discount,
            "price_paid": price_paid,
            "line_total": line_total,
        })
        order_item_id += 1
    order_total[oid] = round2(total)

df_order_items = pd.DataFrame(order_items)
df_order_items.to_csv(RAW_PATH / "order_items.csv", index=False)

# Attach store, totals and an order status to the orders table.
orders_df["store_id"] = orders_df["order_id"].map(order_store).astype("Int64")
orders_df["total_amount"] = orders_df["order_id"].map(order_total).fillna(0.0)
status = rng.choice(
    ["completed", "cancelled"], size=len(orders_df), p=[0.97, 0.03]
)
orders_df["order_status"] = status
orders_df = orders_df[
    ["order_id", "customer_id", "store_id", "order_date", "channel", "order_status", "total_amount"]
]
orders_df.to_csv(RAW_PATH / "orders.csv", index=False)

# --- Promotions reference table ---------------------------------------------

promo_rows = []
promo_id = 1
for year in range(ORDER_START_DATE.year, ORDER_END_DATE.year + 1):
    for p in PROMOTIONS:
        promo_rows.append({
            "promo_id": promo_id,
            "promo_name": p["name"],
            "start_date": date(year, *p["start"]),
            "end_date": date(year, *p["end"]),
            "discount_pct": p["discount_pct"],
            "scope": "all" if p["scope"] == "all" else "|".join(p["scope"]),
        })
        promo_id += 1
pd.DataFrame(promo_rows).to_csv(RAW_PATH / "promotions.csv", index=False)

# --- Shipments (online orders only) -----------------------------------------

ship_methods = list(SHIPPING_METHODS.keys())
ship_method_p = [SHIPPING_METHODS[m]["weight"] for m in ship_methods]

online_orders = orders_df[
    (orders_df["channel"] == "online") & (orders_df["order_status"] == "completed")
]
customer_country = dict(zip(df_customers["customer_id"], df_customers["country"]))

shipments = []
shipment_id = 1
for row in online_orders.itertuples(index=False):
    home_wh = warehouse_by_country[customer_country[row.customer_id]]
    if random.random() < (CROSS_BORDER_FULFILMENT_PROB * 0.15):
        others = [w for w in all_warehouse_ids if w != home_wh]
        warehouse_id = random.choice(others) if others else home_wh
    else:
        warehouse_id = home_wh

    method = random.choices(ship_methods, weights=ship_method_p, k=1)[0]
    spec = SHIPPING_METHODS[method]

    handling = random.randint(1, 2)
    transit = random.randint(spec["min_days"], spec["max_days"])
    if random.random() < LATE_DELIVERY_PROB:
        transit += random.randint(2, 6)

    ship_dt = row.order_date + timedelta(days=handling)
    delivery_dt = ship_dt + timedelta(days=transit)

    if random.random() < FAILED_DELIVERY_PROB:
        delivery_status = "failed"
    elif transit > spec["max_days"]:
        delivery_status = "late"
    else:
        delivery_status = "delivered"

    shipments.append({
        "shipment_id": shipment_id,
        "order_id": row.order_id,
        "warehouse_id": warehouse_id,
        "customer_id": row.customer_id,
        "shipping_method": method,
        "shipping_date": ship_dt,
        "delivery_date": delivery_dt,
        "delivery_status": delivery_status,
        "shipping_cost": 0.0,
    })
    shipment_id += 1

df_shipments = pd.DataFrame(shipments)

# --- Shipment items + shipping cost -----------------------------------------

items_by_order = df_order_items.groupby("order_id")
shipment_items = []
shipment_item_id = 1
shipping_costs = {}

for ship in df_shipments.itertuples(index=False):
    spec = SHIPPING_METHODS[ship.shipping_method]
    total_qty = 0
    if ship.order_id in items_by_order.groups:
        for item in items_by_order.get_group(ship.order_id).itertuples(index=False):
            total_qty += item.quantity
            shipment_items.append({
                "shipment_item_id": shipment_item_id,
                "shipment_id": ship.shipment_id,
                "product_id": item.product_id,
                "quantity": item.quantity,
            })
            shipment_item_id += 1
    shipping_costs[ship.shipment_id] = round2(
        spec["base_cost"] + total_qty * spec["per_unit"] + np.random.uniform(0, 3)
    )

df_shipment_items = pd.DataFrame(shipment_items)
df_shipment_items.to_csv(RAW_PATH / "shipment_items.csv", index=False)
df_shipments["shipping_cost"] = df_shipments["shipment_id"].map(shipping_costs)
df_shipments.to_csv(RAW_PATH / "shipments.csv", index=False)

# --- Returns ----------------------------------------------------------------

order_meta = orders_df.set_index("order_id")[["channel", "order_date"]].to_dict("index")
returns = []
return_id = 1
for item in df_order_items.itertuples(index=False):
    meta = order_meta.get(item.order_id)
    if meta is None:
        continue
    rate = RETURN_RATE[meta["channel"]]
    if random.random() >= rate:
        continue
    qty_returned = random.randint(1, int(item.quantity))
    refund = round2(qty_returned * item.price_paid)
    return_dt = meta["order_date"] + timedelta(days=random.randint(2, RETURN_WINDOW_DAYS))
    reason = random.choices(RETURN_REASONS, weights=RETURN_REASON_WEIGHTS, k=1)[0]
    returns.append({
        "return_id": return_id,
        "order_id": item.order_id,
        "order_item_id": item.order_item_id,
        "product_id": item.product_id,
        "return_date": return_dt.date() if hasattr(return_dt, "date") else return_dt,
        "quantity_returned": qty_returned,
        "refund_amount": refund,
        "reason": reason,
    })
    return_id += 1

pd.DataFrame(returns).to_csv(RAW_PATH / "returns.csv", index=False)

# --- Inventory snapshots (month-end) ----------------------------------------

oi = df_order_items.merge(
    orders_df[["order_id", "store_id", "channel", "order_date", "order_status"]],
    on="order_id", how="left",
)
oi = oi[oi["order_status"] == "completed"]
oi["month"] = oi["order_date"].dt.to_period("M")
months = pd.period_range(ORDER_START_DATE, ORDER_END_DATE, freq="M")


def simulate_inventory(location_ids, product_subsets, sales_df, loc_col,
                       opening_range, reorder_point, target, lead_months=0):
    demand = (
        sales_df.groupby([loc_col, "product_id", "month"])["quantity"]
        .sum().to_dict()
    )
    rows = []
    pending = {}  # (loc, pid) -> month index when replenishment arrives
    for loc in location_ids:
        for pid in product_subsets[loc]:
            stock = int(rng.integers(opening_range[0], opening_range[1] + 1))
            for mi, m in enumerate(months):
                if pending.get((loc, pid)) == mi:
                    stock = max(stock, target)
                    pending.pop((loc, pid), None)
                d = int(demand.get((loc, pid, m), 0))
                sold = min(stock, d)
                stockout = d > stock
                stock -= sold
                rows.append({
                    "snapshot_date": m.to_timestamp(how="end").date(),
                    loc_col: loc,
                    "product_id": pid,
                    "quantity_on_hand": stock,
                    "units_sold": sold,
                    "stockout_flag": int(stockout),
                })
                if stock < reorder_point and (loc, pid) not in pending:
                    if lead_months == 0:
                        stock = target
                    else:
                        pending[(loc, pid)] = mi + lead_months
    return pd.DataFrame(rows)


store_ids = df_stores["store_id"].tolist()
store_subsets = {sid: store_products[sid] for sid in store_ids}
store_sales = oi[oi["channel"] == "in_store"]
df_store_inv = simulate_inventory(
    store_ids, store_subsets, store_sales, "store_id",
    STORE_OPENING_STOCK_RANGE, STORE_REORDER_POINT, STORE_REPLENISH_TARGET,
)
df_store_inv.to_csv(RAW_PATH / "store_inventory.csv", index=False)

order_to_wh = dict(zip(df_shipments["order_id"], df_shipments["warehouse_id"]))
wh_sales = oi[oi["channel"] == "online"].copy()
wh_sales["warehouse_id"] = wh_sales["order_id"].map(order_to_wh)
wh_sales = wh_sales.dropna(subset=["warehouse_id"])
wh_sales["warehouse_id"] = wh_sales["warehouse_id"].astype(int)
wh_subsets = {wid: set(product_ids) for wid in all_warehouse_ids}
df_wh_inv = simulate_inventory(
    all_warehouse_ids, wh_subsets, wh_sales, "warehouse_id",
    WAREHOUSE_OPENING_STOCK_RANGE, WAREHOUSE_REORDER_POINT,
    WAREHOUSE_REPLENISH_TARGET, lead_months=WAREHOUSE_LEAD_TIME_MONTHS,
)
df_wh_inv.to_csv(RAW_PATH / "warehouse_inventory.csv", index=False)

print("Data generation complete:")
for f in sorted(RAW_PATH.glob("*.csv")):
    print(f"  {f.name}")
