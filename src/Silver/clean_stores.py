import pandas as pd
from pathlib import Path

BRONZE = Path("data/03_bronze")
SILVER = Path("data/04_silver")

def clean_stores():

    df = pd.read_csv(BRONZE / "stores.csv")

    df = df.drop_duplicates()

    df["store_name"] = df["store_name"].str.strip()
    df["store_name"] = df["store_name"].str.replace(r"\s+", " ", regex=True)
    df["store_name"] = df["store_name"].str.title()

    df["city"] = df["city"].str.strip()
    city_fix = {
        "Madrd": "Madrid",
        "Sevill": "Seville",
        "Barcelna": "Barcelona"
    }
    df["city"] = df["city"].replace(city_fix)

    df["country"] = df["country"].str.strip().str.title()
    

    df.to_csv(SILVER / "stores.csv", index=False)

if __name__ == "__main__":
    clean_stores()