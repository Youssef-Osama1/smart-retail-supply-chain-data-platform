import pandas as pd
from pathlib import Path

BRONZE = Path("data/03_bronze")
SILVER = Path("data/04_silver")

# Guardrail against the injected 999999 "system bug" rows only. Realistic stock
# sits far below this, so legitimate variation (including zeros) is preserved.
MAX_STOCK = 100_000


def clean_warehouse_inventory():

    df = pd.read_csv(BRONZE / "warehouse_inventory.csv")

    df = df.drop_duplicates()

    df["snapshot_date"] = pd.to_datetime(df["snapshot_date"], errors="coerce")

    df["quantity_on_hand"] = pd.to_numeric(df["quantity_on_hand"], errors="coerce")
    df["quantity_on_hand"] = df["quantity_on_hand"].clip(lower=0)
    df.loc[df["quantity_on_hand"] > MAX_STOCK, "quantity_on_hand"] = MAX_STOCK
    df = df[df["quantity_on_hand"].notna()]
    df["quantity_on_hand"] = df["quantity_on_hand"].astype(int)

    for col in ("units_sold", "stockout_flag"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    df = df.reset_index(drop=True)
    df.to_csv(SILVER / "warehouse_inventory.csv", index=False)


if __name__ == "__main__":
    clean_warehouse_inventory()
