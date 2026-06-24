import sys
import logging
from pathlib import Path

import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger("dq")

SILVER = Path("data/04_silver")


class DQError(AssertionError):
    """Raised when one or more data-quality checks fail."""


def _load():
    return {p.stem: pd.read_csv(p) for p in SILVER.glob("*.csv")}


def run_checks(silver_dir: Path = SILVER):
    global SILVER
    SILVER = Path(silver_dir)
    t = _load()
    failures = []

    def check(name, condition, detail=""):
        if condition:
            log.info("PASS  %s", name)
        else:
            log.error("FAIL  %s %s", name, detail)
            failures.append(name)

    # primary-key uniqueness
    pk = {
        "customers": "customer_id",
        "products": "product_id",
        "stores": "store_id",
        "warehouses": "warehouse_id",
        "orders": "order_id",
        "order_items": "order_item_id",
        "shipments": "shipment_id",
        "shipment_items": "shipment_item_id",
        "returns": "return_id",
        "promotions": "promo_id",
    }
    for table, key in pk.items():
        if table in t:
            dup = t[table][key].duplicated().sum()
            check(f"pk_unique:{table}.{key}", dup == 0, f"({dup} duplicates)")

    # not-null on keys
    for table, key in pk.items():
        if table in t:
            nulls = t[table][key].isna().sum()
            check(f"not_null:{table}.{key}", nulls == 0, f"({nulls} nulls)")

    # referential integrity
    def fk(child, col, parent, pcol):
        if child in t and parent in t:
            missing = ~t[child][col].dropna().isin(set(t[parent][pcol]))
            n = int(missing.sum())
            check(f"fk:{child}.{col}->{parent}.{pcol}", n == 0, f"({n} orphans)")

    fk("order_items", "order_id", "orders", "order_id")
    fk("order_items", "product_id", "products", "product_id")
    fk("orders", "customer_id", "customers", "customer_id")
    fk("shipments", "order_id", "orders", "order_id")
    fk("shipment_items", "shipment_id", "shipments", "shipment_id")
    fk("shipment_items", "product_id", "products", "product_id")
    fk("returns", "order_item_id", "order_items", "order_item_id")

    # no negatives after cleaning
    def non_negative(table, col):
        if table in t and col in t[table]:
            bad = int((pd.to_numeric(t[table][col], errors="coerce") < 0).sum())
            check(f"range>=0:{table}.{col}", bad == 0, f"({bad} negatives)")

    non_negative("order_items", "quantity")
    non_negative("order_items", "price_paid")
    non_negative("products", "unit_price")
    non_negative("products", "cost")
    non_negative("shipments", "shipping_cost")
    non_negative("store_inventory", "quantity_on_hand")
    non_negative("warehouse_inventory", "quantity_on_hand")
    non_negative("returns", "refund_amount")

    # online orders must not have a store_id
    if "orders" in t:
        online_with_store = int(
            ((t["orders"]["channel"] == "online") & t["orders"]["store_id"].notna()).sum()
        )
        check("rule:online_no_store", online_with_store == 0, f"({online_with_store} rows)")

    log.info("Row counts: %s", {k: len(v) for k, v in sorted(t.items())})

    if failures:
        raise DQError(f"{len(failures)} data-quality check(s) failed: {failures}")
    log.info("All data-quality checks passed (%d tables).", len(t))
    return True


if __name__ == "__main__":
    try:
        run_checks()
    except DQError as e:
        log.error(str(e))
        sys.exit(1)
