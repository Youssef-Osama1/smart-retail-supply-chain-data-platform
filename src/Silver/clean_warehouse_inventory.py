import pandas as pd
from pathlib import Path

BRONZE = Path("data/03_bronze")
SILVER = Path("data/04_silver")

MAX_STOCK = 1000

def clean_warehouse_inventory():

    df = pd.read_csv(BRONZE / "warehouse_inventory.csv")

    df = df.drop_duplicates()

    df["quantity_on_hand"] = pd.to_numeric(df["quantity_on_hand"], errors="coerce")

    df["quantity_on_hand"] = df["quantity_on_hand"].abs()

    df.loc[df["quantity_on_hand"] > MAX_STOCK, "quantity_on_hand"] = MAX_STOCK

    df["quantity_on_hand"] = df["quantity_on_hand"].astype(int)

    df.to_csv(SILVER / "warehouse_inventory.csv", index=False)


if __name__ == "__main__":
    clean_warehouse_inventory()