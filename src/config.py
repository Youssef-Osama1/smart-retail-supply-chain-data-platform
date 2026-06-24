from datetime import date

SEED = 42
REFERENCE_DATE = date(2025, 12, 31)  # fixed "as of" date for age calculations

# ---------------------------------------------------------------------------
# Entity volumes
# ---------------------------------------------------------------------------

N_STORES = 20
N_PRODUCTS = 100
N_CUSTOMERS = 25_000
MAX_ORDERS = 250_000

# ---------------------------------------------------------------------------
# Geography
# ---------------------------------------------------------------------------

COUNTRY_CITY_MAP = {
    "Spain": ["Madrid", "Barcelona", "Valencia", "Seville"],
    "Italy": ["Milan", "Rome", "Naples", "Florence"],
    "UK": ["London", "Manchester", "Birmingham", "Liverpool"],
}

# ---------------------------------------------------------------------------
# Products
# ---------------------------------------------------------------------------

ZARA_CATEGORIES = {
    "Women": ["Dresses", "Tops", "Skirts", "Coats"],
    "Men": ["Shirts", "T-Shirts", "Jackets", "Jeans"],
    "Kids": ["T-Shirts", "Hoodies", "Pants"],
    "Accessories": ["Bags", "Shoes"],
}
STYLES = ["Slim Fit", "Oversized", "Regular Fit", "Cropped", "Wide Leg"]

FABRIC_BY_CATEGORY = {
    "Dresses": ["Linen", "Cotton", "Polyester"],
    "Tops": ["Cotton", "Linen"],
    "Skirts": ["Denim", "Polyester"],
    "Coats": ["Wool", "Polyester"],
    "Shirts": ["Cotton", "Linen"],
    "T-Shirts": ["Cotton"],
    "Jackets": ["Denim", "Wool"],
    "Jeans": ["Denim"],
    "Hoodies": ["Cotton", "Polyester"],
    "Pants": ["Cotton", "Denim"],
    "Bags": ["Leather", "Polyester"],
    "Shoes": ["Leather"],
}

SINGULAR_MAP = {
    "Dresses": "Dress",
    "Tops": "Top",
    "Skirts": "Skirt",
    "Coats": "Coat",
    "Shirts": "Shirt",
    "T-Shirts": "T-Shirt",
    "Jackets": "Jacket",
    "Jeans": "Jean",
    "Hoodies": "Hoodie",
    "Pants": "Pant",
    "Bags": "Bag",
    "Shoes": "Shoe",
}

PRICE_RANGES = {
    "Dresses": (50, 150),
    "Tops": (25, 60),
    "Skirts": (40, 90),
    "Coats": (100, 250),
    "Shirts": (30, 70),
    "T-Shirts": (20, 50),
    "Jackets": (80, 200),
    "Jeans": (60, 120),
    "Hoodies": (40, 90),
    "Pants": (35, 80),
    "Bags": (50, 180),
    "Shoes": (70, 220),
}

COGS_RATIO_RANGE = (0.40, 0.60)  # COGS as fraction of list price

SEGMENT_WEIGHTS = {
    "Women": 0.40,
    "Men": 0.30,
    "Kids": 0.20,
    "Accessories": 0.10,
}

# ---------------------------------------------------------------------------
# Customers
# ---------------------------------------------------------------------------

GENDERS = ["Male", "Female"]
GENDER_WEIGHTS = {"Female": 0.62, "Male": 0.38}

AGE_BANDS = {
    (16, 17): 0.05,
    (18, 30): 0.40,
    (31, 45): 0.30,
    (46, 60): 0.18,
    (61, 75): 0.07,
}

LEGACY_CUSTOMER_FRACTION = 0.55  # fraction who signed up before the order window
IN_SEGMENT_PROB = 0.70           # probability of buying from own segment vs cross-shopping

# ---------------------------------------------------------------------------
# Order window & demand model
# ---------------------------------------------------------------------------

ORDER_START_DATE = date(2023, 1, 1)
ORDER_END_DATE = date(2025, 12, 31)

CHANNELS = ["in_store", "online"]
ORDER_CHANNEL_WEIGHTS = {"in_store": 0.65, "online": 0.35}

BASE_DAILY_ORDERS = 60
YEARLY_GROWTH = 0.18

# Mon=0 .. Sun=6
WEEKDAY_FACTORS = {
    0: 0.85,
    1: 0.85,
    2: 0.90,
    3: 0.95,
    4: 1.15,
    5: 1.45,
    6: 1.25,
}

MONTH_FACTORS = {
    1: 1.10,   # January sales
    2: 0.85,
    3: 0.95,
    4: 1.00,
    5: 1.05,
    6: 1.10,   # summer
    7: 1.15,   # summer sale
    8: 0.95,
    9: 1.05,   # back to season / new collection
    10: 1.05,
    11: 1.35,  # Black Friday build-up
    12: 1.55,  # Christmas peak
}

PROMOTIONS = [
    {
        "name": "Winter Sale",
        "start": (1, 2), "end": (1, 31),
        "discount_pct": 0.30, "scope": "all",
        "demand_multiplier": 1.4,
    },
    {
        "name": "Summer Sale",
        "start": (7, 1), "end": (7, 31),
        "discount_pct": 0.35, "scope": "all",
        "demand_multiplier": 1.5,
    },
    {
        "name": "Black Friday",
        "start": (11, 24), "end": (11, 30),
        "discount_pct": 0.40, "scope": "all",
        "demand_multiplier": 2.2,
    },
    {
        "name": "Christmas",
        "start": (12, 15), "end": (12, 26),
        "discount_pct": 0.20,
        "scope": ["Coats", "Jackets", "Bags", "Shoes"],
        "demand_multiplier": 1.6,
    },
]

# ---------------------------------------------------------------------------
# Basket composition
# ---------------------------------------------------------------------------

MIN_ITEMS_PER_ORDER = 1
MAX_ITEMS_PER_ORDER = 5

QUANTITY_WEIGHTS = {1: 0.70, 2: 0.20, 3: 0.10}

SEASONAL_CATEGORIES = {
    "winter": ["Coats", "Jackets", "Hoodies"],
    "summer": ["Dresses", "T-Shirts", "Skirts"],
}
SEASONAL_BIAS = 0.60

# ---------------------------------------------------------------------------
# Inventory & replenishment
# ---------------------------------------------------------------------------

STORE_OPENING_STOCK_RANGE = (10, 45)
WAREHOUSE_OPENING_STOCK_RANGE = (80, 320)

STORE_PRODUCT_COVERAGE = 0.70  # each store carries ~70% of the catalog

STORE_REORDER_POINT = 8
STORE_REPLENISH_TARGET = 40
WAREHOUSE_REORDER_POINT = 70
WAREHOUSE_REPLENISH_TARGET = 280
WAREHOUSE_LEAD_TIME_MONTHS = 1

# ---------------------------------------------------------------------------
# Shipments
# ---------------------------------------------------------------------------

SHIPPING_METHODS = {
    "standard": {"weight": 0.75, "base_cost": 4.0, "per_unit": 1.5, "min_days": 3, "max_days": 7},
    "express":  {"weight": 0.25, "base_cost": 9.0, "per_unit": 2.5, "min_days": 1, "max_days": 3},
}

LATE_DELIVERY_PROB = 0.08
FAILED_DELIVERY_PROB = 0.02
CROSS_BORDER_FULFILMENT_PROB = 0.5

# ---------------------------------------------------------------------------
# Returns
# ---------------------------------------------------------------------------

RETURN_RATE = {"in_store": 0.06, "online": 0.18}

RETURN_REASONS = [
    "wrong_size",
    "not_as_described",
    "damaged",
    "changed_mind",
    "late_delivery",
]
RETURN_REASON_WEIGHTS = [0.40, 0.15, 0.10, 0.25, 0.10]

# How long after delivery / purchase a return is filed.
RETURN_WINDOW_DAYS = 30

INVENTORY_SNAPSHOT_FREQ = "ME"  # pandas month-end
