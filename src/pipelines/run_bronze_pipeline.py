import subprocess
import sys
import os
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

env = os.environ.copy()
env["PYTHONPATH"] = str(PROJECT_ROOT)


def run_script(script_path):
    print(f"Running {script_path}...")
    
    result = subprocess.run(
        [sys.executable, script_path],
        env=env
    )

    if result.returncode != 0:
        print(f"Error running {script_path}")
        sys.exit(1)


def run_bronze_pipeline():

    run_script("src/Bronze/01_generate_data.py")
    run_script("src/Bronze/02_inject_dirty_data.py")
    run_script("src/Bronze/03_bronze_load.py")

    print("Bronze Pipeline Completed Successfully")


if __name__ == "__main__":
    run_bronze_pipeline()