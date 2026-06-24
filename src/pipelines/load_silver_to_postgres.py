import pandas as pd
from sqlalchemy import create_engine, text
from pathlib import Path
from dotenv import load_dotenv
import os

SILVER_PATH = Path("data/04_silver")

load_dotenv()
engine = create_engine(os.getenv("DATABASE_URL"))

tables = [
    "customers",
    "orders",
    "order_items",
    "products",
    "promotions",
    "shipments",
    "shipment_items",
    "stores",
    "store_inventory",
    "warehouses",
    "warehouse_inventory",
    "returns",
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

    print(f"{table} loaded successfully")


def main():
    with engine.begin() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS silver"))

    for table in tables:
        load_table(table)


if __name__ == "__main__":
    main()