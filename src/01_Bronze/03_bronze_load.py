import pandas as pd
from pathlib import Path

RAW_PATH = Path("data/02_raw")
BRONZE_PATH = Path("data/03_bronze")

BRONZE_PATH.mkdir(parents=True, exist_ok=True)

for file in RAW_PATH.glob("*.csv"):
    df = pd.read_csv(file)
    output_path = BRONZE_PATH / file.name
    df.to_csv(output_path, index=False)
