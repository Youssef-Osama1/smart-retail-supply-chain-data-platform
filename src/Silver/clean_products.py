import pandas as pd
from pathlib import Path

BRONZE = Path("data/03_bronze")
SILVER = Path("data/04_silver")

def clean_products():

    df = pd.read_csv(BRONZE / "products.csv")

    df = df.drop_duplicates()

    df["product_name"] = (df["product_name"].astype(str).str.strip().str.replace(r"\s+", " ", regex=True).str.title())

    df["target_segment"] = (
        df["target_segment"]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    segment_map = {
        "women": "Women",
        "woman": "Women",
        "men": "Men",
        "kids": "Kids",
        "kid": "Kids",
        "accessories": "Accessories"
    }
    df["target_segment"] = df["target_segment"].map(segment_map)

    df["category"] = df["category"].astype(str).str.strip()
    category_map = {
        "dress": "Dresses",
        "tshirt": "T-Shirts",
        "jean": "Jeans",
        "shirt": "Shirts"
    }
    df["category"] = df["category"].replace(category_map)
    df["category"] = df["category"].str.title()

    df["unit_price"] = (df["unit_price"].astype(str).str.replace("$", "", regex=False).str.replace(",", "", regex=False))
    df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce")
    df["unit_price"] = df["unit_price"].abs()

    df = df.reset_index(drop=True)

    df.to_csv(SILVER / "products.csv", index=False)


if __name__ == "__main__":
    clean_products()