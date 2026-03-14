from sqlalchemy import create_engine, text
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()
engine = create_engine(os.getenv("DATABASE_URL"))

SQL_PATH = Path("src/Gold")

files = [
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

with engine.begin() as conn:

    for file in files:

        with open(SQL_PATH / file) as f:
            query = f.read()

        conn.execute(text(query))

        print(f"{file} executed")