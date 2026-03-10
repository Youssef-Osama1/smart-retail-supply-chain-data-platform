import pandas as pd
from pathlib import Path

BRONZE = Path("data/03_bronze")
SILVER = Path("data/04_silver")

def clean_order_items():

    df = pd.read_csv(BRONZE / "order_items.csv")
    products = pd.read_csv(SILVER / "products.csv")
    orders = pd.read_csv(SILVER / "orders.csv")

    df = df.drop_duplicates()

    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
    df = df[df["quantity"].notna()]
    df["quantity"] = df["quantity"].abs()

    valid_orders = set(orders["order_id"])
    df = df[df["order_id"].isin(valid_orders)]

    valid_products = set(products["product_id"])
    df = df[df["product_id"].isin(valid_products)]

    df = df.drop(columns=["unit_price"], errors="ignore")

    df = df.merge(
        products[["product_id", "unit_price"]],
        on="product_id",
        how="left"
    )

    df = df.dropna(subset=["unit_price"])

    df["line_total"] = (df["quantity"] * df["unit_price"]).round(2)

    df = df[["order_item_id", "order_id", "product_id", "quantity", "unit_price", "line_total"]]

    df = df.reset_index(drop=True)

    df.to_csv(SILVER / "order_items.csv", index=False)

    # -------------------------------------
    # Recalculate order totals

    order_totals = (
        df.groupby("order_id")["line_total"]
        .sum()
        .reset_index()
    )

    orders = orders.drop(columns=["total_amount"], errors="ignore")

    orders = orders.merge(order_totals, on="order_id", how="left")

    orders["line_total"] = orders["line_total"].fillna(0)

    orders = orders.rename(columns={"line_total": "total_amount"})

    orders.to_csv(SILVER / "orders.csv", index=False)


if __name__ == "__main__":
    clean_order_items()