from sqlalchemy import create_engine, text
from pathlib import Path

engine = create_engine(
    "postgresql+psycopg2://postgres:Mo380807%23%23@localhost:5432/retail_dw"
)

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