import pandas as pd
from pathlib import Path

BRONZE = Path("data/03_bronze")
SILVER = Path("data/04_silver")


def clean_shipments():

    df = pd.read_csv(BRONZE / "shipments.csv")
    orders = pd.read_csv(SILVER / "orders.csv")

    df = df.drop_duplicates()

    df = df[df["order_id"].isin(set(orders["order_id"]))]

    df["shipping_date"] = pd.to_datetime(df["shipping_date"], format="mixed", errors="coerce")
    df["delivery_date"] = pd.to_datetime(df["delivery_date"], format="mixed", errors="coerce")

    # Repair the injected "delivery before shipping" swap.
    mask = df["delivery_date"] < df["shipping_date"]
    df.loc[mask, ["shipping_date", "delivery_date"]] = (
        df.loc[mask, ["delivery_date", "shipping_date"]].values
    )

    # Shipping cost: clean formatting, take magnitude. We do NOT impute high
    # costs to the mean — express / heavy / failed-redelivery shipments are
    # real and analytically meaningful.
    df["shipping_cost"] = (
        df["shipping_cost"].astype(str).str.replace("$", "", regex=False)
    )
    df["shipping_cost"] = pd.to_numeric(df["shipping_cost"], errors="coerce").abs()

    if "shipping_method" in df.columns:
        df["shipping_method"] = df["shipping_method"].astype(str).str.strip().str.lower()
    if "delivery_status" in df.columns:
        df["delivery_status"] = df["delivery_status"].astype(str).str.strip().str.lower()

    df = df.reset_index(drop=True)
    df.to_csv(SILVER / "shipments.csv", index=False)


if __name__ == "__main__":
    clean_shipments()
