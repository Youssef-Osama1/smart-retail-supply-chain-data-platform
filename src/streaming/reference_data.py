from dataclasses import dataclass
from datetime import date

import numpy as np
import pandas as pd
from sqlalchemy import create_engine, text

from src.config import SEGMENT_WEIGHTS


@dataclass
class ReferenceData:
    product_ids: list
    product_price: dict
    product_category: dict
    products_by_segment: dict
    customer_ids: np.ndarray
    customer_info: dict
    customer_weights: np.ndarray
    stores_by_city: dict
    stores_by_country: dict
    next_order_id: int
    next_order_item_id: int


def _age(dob_str: str) -> int:
    try:
        dob = pd.to_datetime(dob_str).date()
    except Exception:
        return 30
    today = date.today()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))


def load_reference(database_url: str) -> ReferenceData:
    engine = create_engine(database_url)

    products = pd.read_sql("SELECT product_id, target_segment, category, unit_price FROM silver.products", engine)
    customers = pd.read_sql("SELECT customer_id, date_of_birth, gender, city, country FROM silver.customers", engine)
    stores = pd.read_sql("SELECT store_id, city, country FROM silver.stores", engine)

    counts = pd.read_sql(
        "SELECT customer_id, COUNT(*) AS n FROM silver.orders GROUP BY customer_id", engine
    )
    with engine.connect() as conn:
        max_order_id = conn.execute(text("SELECT COALESCE(MAX(order_id), 0) FROM silver.orders")).scalar()
        max_item_id = conn.execute(text("SELECT COALESCE(MAX(order_item_id), 0) FROM silver.order_items")).scalar()
        # If the stream has run before, continue past whatever it already wrote.
        max_order_id = max(max_order_id, _safe_stream_max(conn, "orders_raw", "order_id"))
        max_item_id = max(max_item_id, _safe_stream_max(conn, "order_items_raw", "order_item_id"))

    engine.dispose()

    products_by_segment = {
        seg: products.loc[products["target_segment"] == seg, "product_id"].tolist()
        for seg in SEGMENT_WEIGHTS
    }

    customers = customers.merge(counts, on="customer_id", how="left")
    customers["n"] = customers["n"].fillna(0)
    weights = customers["n"].to_numpy(dtype=float) + 1.0
    weights = weights / weights.sum()

    customer_info = {
        int(r.customer_id): {
            "age": _age(r.date_of_birth),
            "gender": r.gender,
            "country": r.country,
            "city": r.city,
        }
        for r in customers.itertuples(index=False)
    }

    return ReferenceData(
        product_ids=products["product_id"].tolist(),
        product_price=dict(zip(products["product_id"], products["unit_price"])),
        product_category=dict(zip(products["product_id"], products["category"])),
        products_by_segment=products_by_segment,
        customer_ids=customers["customer_id"].to_numpy(),
        customer_info=customer_info,
        customer_weights=weights,
        stores_by_city=stores.groupby("city")["store_id"].apply(list).to_dict(),
        stores_by_country=stores.groupby("country")["store_id"].apply(list).to_dict(),
        next_order_id=int(max_order_id) + 1,
        next_order_item_id=int(max_item_id) + 1,
    )


def _safe_stream_max(conn, table: str, col: str) -> int:
    try:
        val = conn.execute(text(f"SELECT COALESCE(MAX({col}), 0) FROM bronze_stream.{table}")).scalar()
        return int(val or 0)
    except Exception:
        return 0
