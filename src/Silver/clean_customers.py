import pandas as pd
from pathlib import Path

BRONZE = Path("data/03_bronze")
SILVER = Path("data/04_silver")

def clean_customers():

    df = pd.read_csv(BRONZE / "customers.csv")

    df = df.drop_duplicates()

    df["first_name"] = df["first_name"].str.strip()
    df["last_name"] = df["last_name"].str.strip()

    df["first_name"] = df["first_name"].str.title()
    df["last_name"] = df["last_name"].str.title()


    df["gender"] = df["gender"].str.strip().str.lower()
    gender_map = {
        "m": "Male",
        "male": "Male",
        "f": "Female",
        "female": "Female"
    }
    df["gender"] = df["gender"].map(gender_map)


    df["date_of_birth"] = pd.to_datetime(df["date_of_birth"],errors="coerce")


    city_fix = {
        "Madrd": "Madrid",
        "Rom": "Rome",
        "Sevill": "Seville"
    }
    df["city"] = df["city"].replace(city_fix)

    df["country"] = df["country"].str.title()

    df = df.reset_index(drop=True)  

    df.to_csv(SILVER / "customers.csv", index=False)


if __name__ == "__main__":
    clean_customers()