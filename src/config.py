from datetime import date

SEED = 42

N_STORES = 20
N_PRODUCTS = 100
N_CUSTOMERS = 25_000
N_ORDERS = 80_000


COUNTRY_CITY_MAP = {
    "Spain": ["Madrid", "Barcelona", "Valencia", "Seville"],
    "Italy": ["Milan", "Rome", "Naples", "Florence"],
    "UK": ["London", "Manchester", "Birmingham", "Liverpool"]
}


ZARA_CATEGORIES = {
    "Women": ["Dresses", "Tops", "Skirts", "Coats"],
    "Men": ["Shirts", "T-Shirts", "Jackets", "Jeans"],
    "Kids": ["T-Shirts", "Hoodies", "Pants"],
    "Accessories": ["Bags", "Shoes"]
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
    "Shoes": ["Leather"]
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
    "Shoes": "Shoe"
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
    "Shoes": (70, 220)
}


SEGMENT_WEIGHTS = {
    "Women": 0.4,
    "Men": 0.3,
    "Kids": 0.2,
    "Accessories": 0.1
}


GENDERS = ["Male", "Female"]
CHANNELS = ["in_store", "online"]


ORDER_CHANNEL_WEIGHTS = {
    "in_store": 0.65,
    "online": 0.35
}

MIN_ITEMS_PER_ORDER = 1
MAX_ITEMS_PER_ORDER = 5

QUANTITY_WEIGHTS = {
    1: 0.7,
    2: 0.2,
    3: 0.1
}

ORDER_START_DATE = date(2023, 1, 1)
ORDER_END_DATE = date(2025, 12, 31)


STORE_STOCK_RANGE = (20, 150)
WAREHOUSE_STOCK_RANGE = (300, 1200)

STORE_PRODUCT_COVERAGE = 0.7  