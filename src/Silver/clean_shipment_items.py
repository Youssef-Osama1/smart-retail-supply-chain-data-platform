import pandas as pd
from pathlib import Path

BRONZE = Path("data/03_bronze")
SILVER = Path("data/04_silver")


def clean_shipment_items():

    df = pd.read_csv(BRONZE / "shipment_items.csv")
    products = pd.read_csv(SILVER / "products.csv")
    shipments = pd.read_csv(SILVER / "shipments.csv")

    df = df.drop_duplicates()

    # Quantity: numeric, magnitude. We do NOT cap to the order-line maximum —
    # consolidated / multi-unit shipment lines are legitimate, and silently
    # capping corrupts the data.
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
    df = df[df["quantity"].notna()]
    df["quantity"] = df["quantity"].abs().astype(int)

    df = df[df["shipment_id"].isin(set(shipments["shipment_id"]))]
    df = df[df["product_id"].isin(set(products["product_id"]))]

    df = df.reset_index(drop=True)
    df.to_csv(SILVER / "shipment_items.csv", index=False)


if __name__ == "__main__":
    clean_shipment_items()
