# Smart Retail Supply Chain Data Platform

An end-to-end **Data Engineering** project that builds a complete analytics platform for a
fast-fashion retailer (ZARA-style). It simulates a realistic retail and supply-chain business,
processes the data through a **Medallion architecture (Bronze → Silver → Gold)**, serves it as a
**PostgreSQL star schema**, and powers a Power BI dashboard and a machine-learning demand model
on top.

The whole pipeline is orchestrated by **Apache Airflow** and runs with a single command via
**Docker Compose**.

## What this project demonstrates

- Designing and orchestrating a multi-stage data pipeline with Airflow.
- A layered Medallion data architecture with clear responsibilities per layer.
- Dimensional modeling: a Gold star schema (8 dimensions, 5 fact tables) built with **dbt**,
  with referential integrity enforced as dbt tests.
- Data-quality enforcement as a hard gate that fails the pipeline on bad data.
- A fully reproducible, containerized environment (one command to stand everything up).
- A downstream BI layer (Power BI) and a forecasting model (XGBoost) consuming the warehouse.

## Tech stack

| Area | Tools |
|------|-------|
| Orchestration | Apache Airflow 2.10.4 |
| Processing | Python, pandas |
| Streaming | Apache Kafka (KRaft) |
| Storage / Warehouse | PostgreSQL 16 |
| Modeling | dbt (star schema, tests) |
| Infrastructure | Docker, Docker Compose |
| Machine Learning | XGBoost, scikit-learn |
| BI | Power BI |

## Pipeline overview

The Airflow DAG `retail_supply_chain_pipeline` runs the following stages in order. Each stage
depends on the previous one, and the data-quality stage stops the run if any check fails.

| Stage | What it does | Output |
|-------|--------------|--------|
| `generate` | Simulates the business (customers, products, orders, inventory, shipments, returns, promotions) | `data/01_raw_clean/` |
| `inject_dirty` | Degrades the clean data with realistic issues (typos, mixed casing, duplicates, bad types) | `data/02_raw/` |
| `bronze_load` | Lands the raw data unchanged | `data/03_bronze/` |
| `silver_clean` | Cleans, standardizes, deduplicates, and type-casts each entity | `data/04_silver/` |
| `dq_checks` | Validates PK uniqueness, FK integrity, value ranges, and business rules — **fails the run on violation** | — |
| `load_silver_to_postgres` | Loads the Silver tables into the Postgres `silver` schema | `silver.*` |
| `gold_build` | Runs `dbt build` — materializes the Gold star schema (dimensions, facts, indexes) and runs all relationship/uniqueness tests | `gold.*` |

## The Medallion layers

**Bronze** — raw landing zone. Data is stored exactly as received, with no cleaning, so the
original (intentionally dirty) state is always preserved and traceable.

**Silver** — cleaned and conformed. One cleaner per entity handles trimming, casing,
deduplication, value mapping (e.g. `m`/`male` → `Male`), known typo fixes, and type casting.
The Silver tables are then loaded into Postgres.

**Gold** — business-ready dimensional model. A star schema optimized for analytics and BI,
built with **dbt** directly from the Silver schema. The Silver Postgres tables are declared as
dbt *sources*; each dimension and fact is a dbt *model*, so dbt derives the build order from the
`ref()`/`source()` dependency graph instead of a hand-maintained script. Primary keys and the
foreign keys between facts and dimensions are enforced as dbt `unique`/`not_null`/`relationships`
tests, and FK-column indexes are declared in each model's config. The dbt project lives in `dbt/`.

## The simulated business

The generator (`src/Bronze/01_generate_data.py`, parameters in `src/config.py`) is designed to
produce analytically rich data rather than flat random noise:

- **Demand model** — daily order volume reacts to year-over-year growth, weekday, month, and
  promotion multipliers, producing real trend, weekend uplift, and seasonal spikes
  (Black Friday, Christmas, Winter/Summer sales).
- **Customer behavior** — heavy-tailed purchase frequency (a minority of customers drive most
  orders, enabling RFM/CLV analysis), acquisition cohorts, gender and age distributions, and
  geography-aware in-store shopping.
- **Margin** — every product carries a cost (COGS), enabling gross / net / margin analytics.
- **Promotions and pricing** — a promotion calendar discounts items in scope; each line records
  the actual price paid at transaction time, never overwritten with the current list price.
- **Inventory** — month-end snapshots derived from opening stock − sales + replenishment, with
  real stockouts and a reorder / lead-time policy across stores and warehouses.
- **Returns** — channel-dependent return rates (online higher than in-store) with reasons.
- **Shipments** — shipping methods, late and failed deliveries, and cross-border fulfilment.

Runs are fully reproducible: a fixed seed and reference date make every run identical.

Default scale: 25,000 customers, 100 products, 20 stores, up to 250,000 orders over 2023–2025.

## Gold star schema

**Dimensions:** `dim_date`, `dim_customers`, `dim_products`, `dim_stores`, `dim_warehouses`,
`dim_channel`, `dim_promotions`, `dim_location`.

**Facts:**

| Fact | Grain | Key measures |
|------|-------|--------------|
| `fact_sales` | order line | quantity, gross / discount / net / cost / **margin** amounts |
| `fact_returns` | returned line | quantity returned, refund amount, reason |
| `fact_inventory` | snapshot × product × location | quantity on hand, units sold, stockout flag |
| `fact_shipments` | shipment line | quantity, shipping cost, delivery SLA |
| `fact_shipment_summary` | shipment | shipping cost, delivery SLA (no double counting) |

Two gates protect quality. Upstream, the `dq_checks` stage enforces primary-key uniqueness,
referential integrity, non-negative numeric ranges, and business rules (for example, online
orders must not carry a store id) on the Silver data — and **fails the run** on violation. In the
Gold layer, `dbt build` re-validates every primary key and every fact→dimension foreign key as
dbt tests, so a modeling regression surfaces immediately.

## Analytics layer

**Power BI dashboard** — a 7-page report built on the Gold schema, covering sales and revenue,
margin and profitability, returns, inventory and stockouts, shipping performance, and seasonal
demand.

**Demand forecasting (machine learning)** — `notebooks/ZARA_Quantity_Prediction.ipynb` trains an
XGBoost model to forecast monthly quantity sold per product category. It pulls aggregated sales
from the Gold layer and engineers lag features, rolling averages, and cyclical month encodings,
with a time-based train/test split.

## Real-time / streaming layer (Kafka)

Alongside the batch pipeline, the platform has a **streaming-ingestion path** that simulates
live order traffic — the batch pipeline loads history; the stream keeps flowing in real time.

```
order-producer ──▶ Kafka topic `orders` ──▶ order-consumer ──▶ bronze_stream.* (Postgres)
                        │
                   Kafka UI (:8081)
```

- **Producer** (`src/streaming/order_producer.py`) — loads reference data (products, customers,
  stores) from `silver.*`, then continuously emits realistic order events (reusing the same
  demand/basket/promotion logic as the batch generator via `src/config.py`) to the `orders` topic.
  Streamed order ids continue past the batch ids so the two never collide.
- **Consumer** (`src/streaming/order_consumer.py`) — reads the topic and lands each event into a
  separate **streaming Bronze** (`bronze_stream.orders_raw` + `bronze_stream.order_items_raw`).
  Delivery is **at-least-once**: Kafka offsets are committed only after the Postgres write
  succeeds, and every row keeps its `kafka_partition`, `kafka_offset`, and `ingested_at`.
- **Kafka** runs as a single-node **KRaft** broker (no Zookeeper); **Kafka UI** at
  http://localhost:8081 lets you browse the topic and messages live.

**Streaming into Gold.** The streamed orders are folded into the warehouse via dbt: staging views
(`stg_orders`, `stg_order_items`) `UNION` the batch (`silver`) and streamed (`bronze_stream`) orders,
and `fact_sales` builds on top of them with a `source_system` column (`batch` / `stream`) so Power BI
can slice historical vs live. Because dbt is batch, streamed orders appear in Gold **after the next
`dbt build`** (re-run the DAG), and Power BI (Import) then needs a Refresh — a micro-batch model, not
instant. A dbt on-run-start hook keeps the Gold build independent of whether the stream has ever run.

The streaming services are long-running (not Airflow tasks). Start them and watch the stream:

```bash
docker compose up -d --build kafka kafka-ui order-producer order-consumer
# rows should keep increasing:
docker compose exec postgres psql -U airflow -d retail -c "select count(*) from bronze_stream.orders_raw;"
```

> The producer needs `silver.*` populated first (run the batch DAG once). Until then it waits and
> logs that reference data is empty.

## Running it

### Option A — Docker (full platform)

```bash
docker compose up -d --build
```

- Airflow UI: http://localhost:8080 (login `airflow` / `airflow`)
- Un-pause and trigger the `retail_supply_chain_pipeline` DAG, or trigger it from the CLI:

```bash
docker compose run --rm airflow-cli airflow dags trigger retail_supply_chain_pipeline
```

The warehouse is reachable from your machine at
`postgresql://airflow:airflow@localhost:5433/retail` (schemas `silver` and `gold`). Point
Power BI or any SQL client there.

### Option B — Local (no orchestrator)

```bash
pip install -r requirements.txt
cp .env.example .env        # set DATABASE_URL to your Postgres

python -m src.pipelines.run_bronze_pipeline      # generate -> inject -> bronze
python -m src.pipelines.run_silver_pipeline      # clean -> silver
python -m src.quality.dq_checks                  # data-quality gate
python -m src.pipelines.load_silver_to_postgres  # silver -> Postgres

# build the gold star schema with dbt (point it at the host Postgres on 5433)
DBT_HOST=localhost DBT_PORT=5433 dbt build --project-dir dbt --profiles-dir dbt
```

## Project layout

```
src/
  config.py                  # all generator and business parameters
  Bronze/
    01_generate_data.py      # business simulator
    02_inject_dirty_data.py  # realistic data degradation
    03_bronze_load.py        # raw landing
  Silver/                    # one cleaner per entity
  streaming/                 # Kafka producer + consumer (real-time order stream)
  quality/dq_checks.py       # PK / FK / range / rule data-quality gate
  pipelines/                 # stage runners (used by the DAG and locally)
dbt/                         # dbt project: Gold star schema (models, sources, tests)
dags/                        # Airflow DAG
docker/                      # Postgres init scripts + streaming Dockerfile
notebooks/                   # demand-forecasting model
Dockerfile, docker-compose.yml
```
