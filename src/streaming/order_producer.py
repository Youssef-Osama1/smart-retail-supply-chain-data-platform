import json
import logging
import random
import time
import uuid
from datetime import date, datetime, timezone

import numpy as np
from confluent_kafka import Producer
from confluent_kafka.admin import AdminClient, NewTopic

from src.config import (
    ORDER_CHANNEL_WEIGHTS, QUANTITY_WEIGHTS, PROMOTIONS,
    MIN_ITEMS_PER_ORDER, MAX_ITEMS_PER_ORDER, IN_SEGMENT_PROB,
    SEASONAL_CATEGORIES, SEASONAL_BIAS,
)
from src.streaming import config
from src.streaming.reference_data import load_reference

logging.basicConfig(level=logging.INFO, format="%(asctime)s [producer] %(message)s")
log = logging.getLogger(__name__)

rng = np.random.default_rng()


def eligible_pools(ref, age, gender):
    by_seg = ref.products_by_segment
    if age < 18:
        return by_seg.get("Kids", []), by_seg.get("Accessories", [])
    if gender == "Female":
        return by_seg.get("Women", []), by_seg.get("Accessories", []) + by_seg.get("Men", [])
    return by_seg.get("Men", []), by_seg.get("Accessories", []) + by_seg.get("Women", [])


def season_of(month):
    if month in (11, 12, 1, 2):
        return "winter"
    if month in (5, 6, 7, 8):
        return "summer"
    return "normal"


def active_promo(d):
    for promo in PROMOTIONS:
        start = date(d.year, *promo["start"])
        end = date(d.year, *promo["end"])
        if start <= d <= end:
            return promo
    return None


def build_order(ref, ids):
    customer_id = int(rng.choice(ref.customer_ids, p=ref.customer_weights))
    cust = ref.customer_info[customer_id]

    channel = random.choices(list(ORDER_CHANNEL_WEIGHTS), weights=list(ORDER_CHANNEL_WEIGHTS.values()))[0]
    if channel == "in_store":
        pool = ref.stores_by_city.get(cust["city"]) or ref.stores_by_country.get(cust["country"])
        store_id = int(random.choice(pool)) if pool else None
    else:
        store_id = None

    now = datetime.now(timezone.utc)
    primary, secondary = eligible_pools(ref, cust["age"], cust["gender"])
    season = season_of(now.month)
    promo = active_promo(now.date())

    n_items = random.randint(MIN_ITEMS_PER_ORDER, MAX_ITEMS_PER_ORDER)
    qty_values = list(QUANTITY_WEIGHTS)
    qty_p = list(QUANTITY_WEIGHTS.values())

    chosen, attempts = set(), 0
    while len(chosen) < n_items and attempts < n_items * 6:
        attempts += 1
        candidates = primary if random.random() < IN_SEGMENT_PROB else secondary
        if not candidates:
            candidates = ref.product_ids
        pid = random.choice(candidates)
        if season != "normal" and random.random() < SEASONAL_BIAS:
            if ref.product_category[pid] not in SEASONAL_CATEGORIES[season]:
                continue
        chosen.add(pid)

    items, total = [], 0.0
    for pid in chosen:
        qty = random.choices(qty_values, weights=qty_p)[0]
        list_price = float(ref.product_price[pid])
        discount = 0.0
        if promo and (promo["scope"] == "all" or ref.product_category[pid] in promo["scope"]):
            discount = promo["discount_pct"]
        price_paid = round(list_price * (1 - discount), 2)
        line_total = round(qty * price_paid, 2)
        total += line_total
        items.append({
            "order_item_id": ids[1],
            "product_id": int(pid),
            "quantity": int(qty),
            "unit_price": list_price,
            "discount_pct": discount,
            "price_paid": price_paid,
            "line_total": line_total,
        })
        ids[1] += 1

    order = {
        "order_id": ids[0],
        "customer_id": customer_id,
        "store_id": store_id,
        "order_date": now.isoformat(),
        "channel": channel,
        "order_status": "completed" if random.random() < 0.97 else "cancelled",
        "total_amount": round(total, 2),
    }
    ids[0] += 1

    return {
        "event_id": str(uuid.uuid4()),
        "event_type": "order_created",
        "produced_at": now.isoformat(),
        "order": order,
        "items": items,
    }


def wait_for_kafka(admin, retries=30, delay=2):
    for i in range(retries):
        try:
            admin.list_topics(timeout=5)
            return
        except Exception as e:
            log.info("waiting for Kafka (%s/%s): %s", i + 1, retries, e)
            time.sleep(delay)
    raise RuntimeError("Kafka not reachable")


def ensure_topic(admin):
    md = admin.list_topics(timeout=5)
    if config.ORDERS_TOPIC in md.topics:
        return
    topic = NewTopic(
        config.ORDERS_TOPIC,
        num_partitions=config.ORDERS_TOPIC_PARTITIONS,
        replication_factor=config.ORDERS_TOPIC_REPLICATION,
    )
    for tname, fut in admin.create_topics([topic]).items():
        try:
            fut.result()
            log.info("created topic %s (%s partitions)", tname, config.ORDERS_TOPIC_PARTITIONS)
        except Exception as e:
            log.info("topic %s: %s", tname, e)


def delivery_report(err, msg):
    if err is not None:
        log.warning("delivery failed: %s", err)


def load_reference_when_ready(delay=3):
    """Load reference data, waiting until silver.* is populated (batch has run)."""
    while True:
        try:
            ref = load_reference(config.DATABASE_URL)
            if len(ref.customer_ids) > 0 and len(ref.product_ids) > 0:
                return ref
            log.info("silver.* is empty (run the batch pipeline first); retrying in %ss", delay)
        except Exception as e:
            log.info("waiting for silver reference data: %s", e)
        time.sleep(delay)


def main():
    admin = AdminClient({"bootstrap.servers": config.KAFKA_BOOTSTRAP_SERVERS})
    wait_for_kafka(admin)
    ensure_topic(admin)

    log.info("loading reference data from silver...")
    ref = load_reference_when_ready()
    ids = [ref.next_order_id, ref.next_order_item_id]
    log.info("reference loaded; starting order ids at order_id=%s item_id=%s", ids[0], ids[1])

    producer = Producer({"bootstrap.servers": config.KAFKA_BOOTSTRAP_SERVERS})
    interval = 1.0 / config.ORDERS_PER_SECOND if config.ORDERS_PER_SECOND > 0 else 0.5

    while True:
        event = build_order(ref, ids)
        producer.produce(
            config.ORDERS_TOPIC,
            key=str(event["order"]["order_id"]),
            value=json.dumps(event, default=str),
            callback=delivery_report,
        )
        producer.poll(0)
        log.info(
            "order_id=%s customer=%s channel=%s items=%d total=%.2f",
            event["order"]["order_id"], event["order"]["customer_id"],
            event["order"]["channel"], len(event["items"]), event["order"]["total_amount"],
        )
        time.sleep(interval)


if __name__ == "__main__":
    main()
