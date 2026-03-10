import pandas as pd
from pathlib import Path

BRONZE = Path("data/03_bronze")
SILVER = Path("data/04_silver")

MAX_REASONABLE_COST = 100

def clean_shipments():

    df = pd.read_csv(BRONZE / "shipments.csv")
    orders = pd.read_csv(SILVER / "orders.csv")

    df = df.drop_duplicates()

    valid_orders = set(orders["order_id"])
    df = df[df["order_id"].isin(valid_orders)]

    df["shipping_date"] = pd.to_datetime(df["shipping_date"], format="mixed", errors="coerce")

    df["delivery_date"] = pd.to_datetime(df["delivery_date"], format="mixed", errors="coerce")

    mask = df["delivery_date"] < df["shipping_date"]
    temp = df.loc[mask, "shipping_date"]
    df.loc[mask, "shipping_date"] = df.loc[mask, "delivery_date"]
    df.loc[mask, "delivery_date"] = temp

    df["shipping_cost"] = (df["shipping_cost"].astype(str).str.replace("$", "", regex=False))
    df["shipping_cost"] = pd.to_numeric(df["shipping_cost"], errors="coerce")
    df["shipping_cost"] = df["shipping_cost"].abs()

    mean_cost = df.loc[df["shipping_cost"] <= MAX_REASONABLE_COST, "shipping_cost"].mean()
    df.loc[df["shipping_cost"] > MAX_REASONABLE_COST, "shipping_cost"] = mean_cost

    df = df.reset_index(drop=True)

    df.to_csv(SILVER / "shipments.csv", index=False)


if __name__ == "__main__":
    clean_shipments()