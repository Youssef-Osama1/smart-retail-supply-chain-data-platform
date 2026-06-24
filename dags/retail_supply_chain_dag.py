from __future__ import annotations

import sys
import logging
from datetime import timedelta
from pathlib import Path

import pendulum
from airflow.decorators import dag, task

# Make the project importable inside the Airflow worker.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

log = logging.getLogger(__name__)

default_args = {
    "owner": "data-eng",
    "retries": 2,
    "retry_delay": timedelta(minutes=2),
}


@dag(
    dag_id="retail_supply_chain_pipeline",
    description="Generate -> Bronze -> Silver -> DQ -> Postgres -> Gold star schema",
    schedule="@daily",
    start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
    catchup=False,
    default_args=default_args,
    tags=["retail", "medallion", "supply-chain"],
)
def retail_supply_chain_pipeline():

    @task
    def generate():
        import runpy
        runpy.run_path(str(PROJECT_ROOT / "src/Bronze/01_generate_data.py"), run_name="__main__")

    @task
    def inject_dirty():
        import runpy
        runpy.run_path(str(PROJECT_ROOT / "src/Bronze/02_inject_dirty_data.py"), run_name="__main__")

    @task
    def bronze_load():
        import runpy
        runpy.run_path(str(PROJECT_ROOT / "src/Bronze/03_bronze_load.py"), run_name="__main__")

    @task
    def silver_clean():
        from src.pipelines.run_silver_pipeline import run_silver_pipeline
        run_silver_pipeline()

    @task
    def dq_checks():
        from src.quality.dq_checks import run_checks
        run_checks()

    @task
    def load_silver_to_postgres():
        from src.pipelines.load_silver_to_postgres import main
        main()

    @task
    def gold_build():
        import runpy
        runpy.run_path(str(PROJECT_ROOT / "src/pipelines/run_gold_pipeline.py"), run_name="__main__")

    (
        generate()
        >> inject_dirty()
        >> bronze_load()
        >> silver_clean()
        >> dq_checks()
        >> load_silver_to_postgres()
        >> gold_build()
    )


retail_supply_chain_pipeline()
