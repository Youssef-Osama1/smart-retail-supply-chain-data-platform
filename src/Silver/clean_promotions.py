import pandas as pd
from pathlib import Path

BRONZE = Path("data/03_bronze")
SILVER = Path("data/04_silver")


def clean_promotions():

    df = pd.read_csv(BRONZE / "promotions.csv")

    df = df.drop_duplicates()

    df["promo_name"] = df["promo_name"].astype(str).str.strip().str.title()
    df["start_date"] = pd.to_datetime(df["start_date"], errors="coerce")
    df["end_date"] = pd.to_datetime(df["end_date"], errors="coerce")
    df["discount_pct"] = pd.to_numeric(df["discount_pct"], errors="coerce").clip(0, 1)
    df["scope"] = df["scope"].astype(str).str.strip()

    df = df.reset_index(drop=True)
    df.to_csv(SILVER / "promotions.csv", index=False)


if __name__ == "__main__":
    clean_promotions()
