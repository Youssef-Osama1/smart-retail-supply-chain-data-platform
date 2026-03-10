import pandas as pd
from pathlib import Path
from src.config import QUANTITY_WEIGHTS

BRONZE = Path("data/03_bronze")
SILVER = Path("data/04_silver")

MAX_QUANTITY = max(QUANTITY_WEIGHTS.keys())

def clean_shipment_items():

    df = pd.read_csv(BRONZE / "shipment_items.csv")

    products = pd.read_csv(SILVER / "products.csv")
    shipments = pd.read_csv(SILVER / "shipments.csv")

    df = df.drop_duplicates()


    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
    df["quantity"] = df["quantity"].abs()

    df.loc[df["quantity"] > MAX_QUANTITY, "quantity"] = MAX_QUANTITY
    df["quantity"] = df["quantity"].astype(int)

    valid_shipments = set(shipments["shipment_id"])
    df = df[df["shipment_id"].isin(valid_shipments)]

    valid_products = set(products["product_id"])
    df = df[df["product_id"].isin(valid_products)]

    df = df.reset_index(drop=True)

    df.to_csv(SILVER / "shipment_items.csv", index=False)


if __name__ == "__main__":
    clean_shipment_items()