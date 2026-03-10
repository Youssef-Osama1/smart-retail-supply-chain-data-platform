import pandas as pd
from pathlib import Path

BRONZE = Path("data/03_bronze")
SILVER = Path("data/04_silver")

def clean_store_inventory():

    df = pd.read_csv(BRONZE / "store_inventory.csv")

    df = df.drop_duplicates()

    df["quantity_on_hand"] = pd.to_numeric(df["quantity_on_hand"], errors="coerce")
    df["quantity_on_hand"] = df["quantity_on_hand"].abs().astype(float)

    mean_qty = df.loc[df["quantity_on_hand"] > 0, "quantity_on_hand"].mean()
    df.loc[df["quantity_on_hand"] == 0, "quantity_on_hand"] = mean_qty

    df["quantity_on_hand"] = df["quantity_on_hand"].astype(int)

    df.to_csv(SILVER / "store_inventory.csv", index=False)


if __name__ == "__main__":
    clean_store_inventory()