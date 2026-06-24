import pandas as pd
from pathlib import Path

BRONZE = Path("data/03_bronze")
SILVER = Path("data/04_silver")


def clean_returns():

    df = pd.read_csv(BRONZE / "returns.csv")
    order_items = pd.read_csv(SILVER / "order_items.csv")

    df = df.drop_duplicates()

    df["return_date"] = pd.to_datetime(df["return_date"], format="mixed", errors="coerce")

    df["quantity_returned"] = pd.to_numeric(df["quantity_returned"], errors="coerce").abs()
    df = df[df["quantity_returned"].notna()]
    df["quantity_returned"] = df["quantity_returned"].astype(int)

    # Refund amount: clean currency formatting, take magnitude.
    df["refund_amount"] = (
        df["refund_amount"].astype(str)
        .str.replace("$", "", regex=False)
        .str.replace(",", "", regex=False)
    )
    df["refund_amount"] = pd.to_numeric(df["refund_amount"], errors="coerce").abs()

    df["reason"] = df["reason"].astype(str).str.strip().str.lower()

    # Referential integrity: a return must point to a real order line.
    df = df[df["order_item_id"].isin(set(order_items["order_item_id"]))]

    df = df.reset_index(drop=True)
    df.to_csv(SILVER / "returns.csv", index=False)


if __name__ == "__main__":
    clean_returns()
