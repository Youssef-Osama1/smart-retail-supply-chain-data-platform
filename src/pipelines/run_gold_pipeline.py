from sqlalchemy import create_engine, text
from pathlib import Path
from dotenv import load_dotenv
import pandas as pd
import os

load_dotenv()

engine = create_engine(os.getenv("DATABASE_URL"))
PROJECT_ROOT = Path(__file__).resolve().parents[2]


SQL_PATH = Path(f"{PROJECT_ROOT}/src/Gold")
SILVER_PATH = Path(f"{PROJECT_ROOT}/src/data/04_silver")

# All silver tables (must match CSV names)
silver_tables = [
    "customers",
    "products",
    "stores",
    "warehouses",
    "orders",
    "order_items",
    "store_inventory",
    "warehouse_inventory",
    "shipments",
    "shipment_items"
]

sql_files = [
    "create_schema.sql",

    "dim_customers.sql",
    "dim_products.sql",
    "dim_stores.sql",
    "dim_warehouses.sql",
    "dim_date.sql",

    "fact_sales.sql",
    "fact_shipments.sql",
    "fact_inventory.sql",

    "constraints.sql"
]

# Step 1 — Create schemas (separate connection)
with engine.connect() as conn:
    conn.execute(text("CREATE SCHEMA IF NOT EXISTS silver"))
    conn.execute(text("CREATE SCHEMA IF NOT EXISTS gold"))
    conn.commit()

print("Schemas ready!")

# Step 2 — Load Silver CSVs into PostgreSQL
for table in silver_tables:
    df = pd.read_csv(SILVER_PATH / f"{table}.csv")

    df.to_sql(
        table,
        engine,
        schema="silver",
        if_exists="replace",
        index=False
    )

    print(f"Loaded silver.{table}")

#  Step 3 — Execute Gold SQL files
with engine.begin() as conn:

    for file in sql_files:
        print(f"\nRunning {file}...")   #  DEBUG LINE

        with open(SQL_PATH / file) as f:
            query = f.read()

        #  FIX: handle multiple SQL statements
        statements = query.split(";")

        for stmt in statements:
            stmt = stmt.strip()
            if stmt:
                conn.execute(text(stmt))

        print(f"{file} executed!")