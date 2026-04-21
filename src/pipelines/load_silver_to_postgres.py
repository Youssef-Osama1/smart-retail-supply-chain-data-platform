import pandas as pd
from sqlalchemy import create_engine, text
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

engine = create_engine(os.getenv("DATABASE_URL"))

# FIX: absolute path like your gold pipeline
PROJECT_ROOT = Path(__file__).resolve().parents[2]
SILVER_PATH = PROJECT_ROOT / "src" / "pipelines" / "data/04_silver"

tables = [
    "customers",
    "orders",
    "order_items",
    "products",
    "shipments",
    "shipment_items",
    "stores",
    "store_inventory",
    "warehouses",
    "warehouse_inventory"
]


def load_table(table):
    df = pd.read_csv(SILVER_PATH / f"{table}.csv")

    df.to_sql(
        table,
        engine,
        schema="silver",
        if_exists="replace",
        index=False
    )

    print(f"Loaded silver.{table} ✅")


def main():
    # ✅ FIX: create schema BEFORE loading
    with engine.connect() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS silver"))
        conn.commit()

    print("Schema silver ready ✅")

    for table in tables:
        load_table(table)


if __name__ == "__main__":
    main()