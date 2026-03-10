import pandas as pd
from pathlib import Path

BRONZE = Path("data/03_bronze")
SILVER = Path("data/04_silver")

def clean_warehouses():

    df = pd.read_csv(BRONZE / "warehouses.csv")

    df.to_csv(SILVER / "warehouses.csv", index=False)

if __name__ == "__main__":
    clean_warehouses()