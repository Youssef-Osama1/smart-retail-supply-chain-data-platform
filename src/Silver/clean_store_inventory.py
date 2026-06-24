import pandas as pd
from pathlib import Path

BRONZE = Path("data/03_bronze")
SILVER = Path("data/04_silver")


def clean_store_inventory():

    df = pd.read_csv(BRONZE / "store_inventory.csv")

    df = df.drop_duplicates()

    df["snapshot_date"] = pd.to_datetime(df["snapshot_date"], errors="coerce")

    df["quantity_on_hand"] = pd.to_numeric(df["quantity_on_hand"], errors="coerce")
    # Physical stock cannot be negative -> clip to 0. ZERO IS PRESERVED: a
    # zero is a genuine stockout, the most important inventory signal, so we do
    # NOT impute it away with a mean.
    df["quantity_on_hand"] = df["quantity_on_hand"].clip(lower=0)
    df = df[df["quantity_on_hand"].notna()]
    df["quantity_on_hand"] = df["quantity_on_hand"].astype(int)

    for col in ("units_sold", "stockout_flag"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    df = df.reset_index(drop=True)
    df.to_csv(SILVER / "store_inventory.csv", index=False)


if __name__ == "__main__":
    clean_store_inventory()
