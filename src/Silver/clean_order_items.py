import pandas as pd
from pathlib import Path

BRONZE = Path("data/03_bronze")
SILVER = Path("data/04_silver")


def clean_order_items():

    df = pd.read_csv(BRONZE / "order_items.csv")
    products = pd.read_csv(SILVER / "products.csv")
    orders = pd.read_csv(SILVER / "orders.csv")

    df = df.drop_duplicates()

    # Quantity: numeric, drop unparseable, take magnitude.
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
    df = df[df["quantity"].notna()]
    df["quantity"] = df["quantity"].abs().astype(int)

    # Referential integrity against cleaned dimensions.
    df = df[df["order_id"].isin(set(orders["order_id"]))]
    df = df[df["product_id"].isin(set(products["product_id"]))]

    # discount_pct: clean formatting, clamp to [0, 1].
    df["discount_pct"] = pd.to_numeric(df.get("discount_pct"), errors="coerce").fillna(0.0)
    df["discount_pct"] = df["discount_pct"].clip(0, 1)

    # price_paid is the HISTORICAL transaction price. Preserve it; only clean
    # formatting. Do NOT overwrite it with the current product price.
    df["price_paid"] = (
        df["price_paid"].astype(str)
        .str.replace("$", "", regex=False)
        .str.replace(",", "", regex=False)
    )
    df["price_paid"] = pd.to_numeric(df["price_paid"], errors="coerce").abs()

    # unit_price is the product LIST price (a dimension attribute) — safe to
    # refresh from the cleaned product dimension.
    df = df.drop(columns=["unit_price"], errors="ignore")
    df = df.merge(products[["product_id", "unit_price"]], on="product_id", how="left")

    # Where the historical paid price is missing, fall back to list*(1-discount).
    df["price_paid"] = df["price_paid"].fillna(
        (df["unit_price"] * (1 - df["discount_pct"])).round(2)
    )

    df["line_total"] = (df["quantity"] * df["price_paid"]).round(2)

    df = df[[
        "order_item_id", "order_id", "product_id", "quantity",
        "unit_price", "discount_pct", "price_paid", "line_total",
    ]].reset_index(drop=True)

    df.to_csv(SILVER / "order_items.csv", index=False)

    # ---------------------------------------------------------------
    # Recompute order totals from the cleaned line totals.
    order_totals = df.groupby("order_id")["line_total"].sum().reset_index()
    orders = orders.drop(columns=["total_amount"], errors="ignore")
    orders = orders.merge(order_totals, on="order_id", how="left")
    orders["line_total"] = orders["line_total"].fillna(0)
    orders = orders.rename(columns={"line_total": "total_amount"})
    orders.to_csv(SILVER / "orders.csv", index=False)


if __name__ == "__main__":
    clean_order_items()
