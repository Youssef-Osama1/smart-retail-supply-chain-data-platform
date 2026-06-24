# Smart Retail Supply Chain Data Platform

An end-to-end, orchestrated **Medallion (Bronze → Silver → Gold)** data platform for a
fictional fast-fashion retailer ("ZARA"-style). It simulates a realistic retail /
supply-chain business, lands the data through cleaning and modeling layers, and serves a
**PostgreSQL star schema** ready for Power BI dashboards and ML forecasting.

The whole platform runs with one command via Docker + Apache Airflow.

---

## Architecture

```
                    ┌─────────────────────────────────────────────────────────┐
                    │                  Apache Airflow DAG                       │
                    │             retail_supply_chain_pipeline                  │
                    └─────────────────────────────────────────────────────────┘
                                            │
  ┌───────────────┐   ┌───────────────┐   ┌───────────────┐   ┌──────────────┐
  │ Source sim.   │   │   BRONZE      │   │   SILVER      │   │    GOLD      │
  │ generate +    │──▶│ raw, as-is    │──▶│ cleaned,      │──▶│ star schema  │
  │ inject dirt   │   │ (CSV copy)    │   │ typed, tested │   │ (Postgres)   │
  └───────────────┘   └───────────────┘   └───────────────┘   └──────────────┘
   01_raw_clean/        03_bronze/          04_silver/          gold.* tables
   02_raw/                                  + silver.* (PG)     dims + facts
                                                  │
                                            ┌─────▼─────┐
                                            │ DQ gate   │  (PK / FK / ranges)
                                            └───────────┘
                                                  │
                                            ┌─────▼─────┐
                                            │ Power BI  │  margin, returns,
                                            │ / ML      │  seasonality, stockouts
                                            └───────────┘
```

Pipeline stages (Airflow tasks, in order):

| Task | What it does |
|------|--------------|
| `generate` | Simulates the business → `data/01_raw_clean/*.csv` |
| `inject_dirty` | Degrades the data (typos, casing, dupes, bad types) → `data/02_raw/` |
| `bronze_load` | Lands raw data unchanged → `data/03_bronze/` |
| `silver_clean` | Cleans/standardizes/validates → `data/04_silver/` |
| `dq_checks` | PK uniqueness, FK integrity, ranges — **fails the run on violation** |
| `load_silver_to_postgres` | Loads Silver CSVs into Postgres `silver` schema |
| `gold_build` | Builds the `gold` star schema (dims, facts, constraints, indexes) |

---

## The simulated business

The generator (`src/Bronze/01_generate_data.py`, parameters in `src/config.py`) is built to
produce **analytically rich** data, not flat noise:

- **Temporal demand** — daily order volume = baseline × YoY growth × weekday × month ×
  promotion multipliers. Produces real trend, weekend uplift, and Black Friday / Christmas /
  seasonal-sale spikes.
- **Customer heterogeneity** — heavy-tailed purchase frequency (a minority of customers drive
  most orders → meaningful RFM/CLV), acquisition cohorts via `signup_date`.
- **Realistic behavior** — weighted (not hard-coded) segment preferences with cross-shopping;
  gender skew; real birth dates; geography-aware in-store shopping.
- **Margin** — every product has a `cost` (COGS) → gross/net/margin analytics.
- **Promotions & historical price** — a promotion calendar discounts items in scope;
  `order_items.price_paid` records the **actual transaction price** (never overwritten with the
  current list price).
- **Inventory realism** — month-end snapshots derived from `opening stock − sales +
  replenishment`, with real **stockouts** and a reorder/lead-time policy.
- **Returns & refunds** — channel-dependent return rates (online ≫ in-store) with reasons.
- **Shipments** — shipping method (standard/express), late/failed deliveries, occasional
  cross-border fulfilment.

Reproducible: a fixed `SEED` + `REFERENCE_DATE` make every run identical.

---

## Star schema (Gold)

```
                 dim_date ────────────────┐
                    │  ▲                   │
                    │  │                   │
  dim_customers ──┐ │  │ ┌── dim_products  │
                  ▼ ▼  │ ▼                 ▼
                ┌────────────┐        ┌──────────────┐
   dim_channel─▶│ fact_sales │        │fact_inventory│◀─ dim_products
                └────────────┘        └──────────────┘   (+ dim_date)
  dim_stores ──▲                       location_id = store|warehouse
                                       + snapshot_date_key, units_sold, stockout_flag

  fact_returns ── dim_customers / dim_products / dim_date
  fact_shipments / fact_shipment_summary ── dim_customers / dim_warehouses / dim_products / dim_date
  dim_promotions (reference)
```

**Facts**

| Fact | Grain | Key measures |
|------|-------|--------------|
| `fact_sales` | order line | quantity, gross / discount / net / cost / **margin** amounts |
| `fact_returns` | returned line | quantity_returned, refund_amount, reason |
| `fact_inventory` | snapshot × product × location | quantity_on_hand, units_sold, stockout_flag |
| `fact_shipments` | shipment line | quantity (cost/SLA repeat — see note) |
| `fact_shipment_summary` | shipment | shipping_cost, delivery_days (use this for cost/SLA) |

> **Power BI notes:** `dim_date` is a **role-playing** dimension for `fact_shipments`
> (`ship_date_key` vs `delivery_date_key`) — use an inactive relationship + `USERELATIONSHIP`.
> Aggregate shipping cost from `fact_shipment_summary`, not `fact_shipments`, to avoid
> double-counting across shipment lines. `fact_inventory.location_id` is polymorphic
> (store *or* warehouse), so it carries product + date FKs only.

A full column-level **data dictionary** is in [`docs/DATA_DICTIONARY.md`](docs/DATA_DICTIONARY.md).

---

## Running it

### Option A — Docker (full platform)

```bash
docker compose up -d --build
# Airflow UI: http://localhost:8080  (airflow / airflow)
# Un-pause and trigger the DAG "retail_supply_chain_pipeline", or:
docker compose run --rm airflow-cli airflow dags trigger retail_supply_chain_pipeline
```

The warehouse is exposed at `postgresql://airflow:airflow@localhost:5432/retail`
(schemas `silver` and `gold`) — point Power BI / a SQL client there.

### Option B — Local (no orchestrator)

```bash
pip install -r requirements.txt
cp .env.example .env        # set DATABASE_URL to your Postgres

python -m src.pipelines.run_bronze_pipeline      # generate → inject → bronze
python -m src.pipelines.run_silver_pipeline      # clean → silver
python -m src.quality.dq_checks                  # data-quality gate
python -m src.pipelines.load_silver_to_postgres  # silver → Postgres
python -m src.pipelines.run_gold_pipeline        # build gold star schema
```

---

## Project layout

```
src/
  config.py                  # all generator/business parameters
  Bronze/
    01_generate_data.py      # business simulator
    02_inject_dirty_data.py  # realistic data degradation
    03_bronze_load.py        # raw landing
  Silver/                    # one cleaner per entity
  Gold/                      # star-schema DDL (dims, facts, constraints)
  quality/dq_checks.py       # PK/FK/range data-quality gate
  pipelines/                 # stage runners (used by the DAG and locally)
dags/                        # Airflow DAG
docker/                      # Postgres init
Dockerfile, docker-compose.yml
```

---

## Known simplifications

- Products are modeled at **style** grain (no size/color SKU layer).
- Bronze is a CSV pass-through (no separate object store / ingestion metadata).
- Dimensions are rebuilt each run (**no SCD Type 2** history).
- Transformations are pandas + raw SQL (no dbt).

These were deliberate scope choices to keep the project focused and runnable.
```
