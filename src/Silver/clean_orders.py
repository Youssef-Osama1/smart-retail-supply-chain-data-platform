import pandas as pd
from pathlib import Path
import numpy as np
from src.config import ORDER_START_DATE, ORDER_END_DATE

BRONZE = Path("data/03_bronze")
SILVER = Path("data/04_silver")

def clean_orders():

    df = pd.read_csv(BRONZE/"orders.csv")

    df = df.drop_duplicates()
    
    df["channel"] = (df["channel"].astype(str).str.strip().str.lower().str.replace(r"\s+", "_", regex=True))
    df.loc[df["channel"] == "online", "store_id"] = np.nan
    df["store_id"] = df["store_id"].astype("Int64")
    
    df["total_amount"] = (df["total_amount"].astype(str).str.replace("$", "", regex=False).str.replace(",", "", regex=False))
    df["total_amount"] = pd.to_numeric(df["total_amount"],errors="coerce")
    df["total_amount"] = df["total_amount"].abs()

    df["order_date"] = pd.to_datetime(df["order_date"], format="mixed", errors="coerce")
    df = df[(df["order_date"] >= pd.Timestamp(ORDER_START_DATE)) &(df["order_date"] <= pd.Timestamp(ORDER_END_DATE))]

    df = df.reset_index(drop=True)

    df.to_csv(SILVER / "orders.csv", index=False)


if __name__ == "__main__":
    clean_orders()
