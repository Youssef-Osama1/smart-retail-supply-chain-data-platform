import json
import logging
import time

from confluent_kafka import Consumer, KafkaError
from sqlalchemy import create_engine, text

from src.streaming import config

logging.basicConfig(level=logging.INFO, format="%(asctime)s [consumer] %(message)s")
log = logging.getLogger(__name__)

DDL = f"""
CREATE SCHEMA IF NOT EXISTS {config.STREAM_SCHEMA};

CREATE TABLE IF NOT EXISTS {config.STREAM_SCHEMA}.{config.ORDERS_TABLE} (
    event_id       text,
    order_id       bigint,
    customer_id    bigint,
    store_id       bigint,
    order_date     timestamptz,
    channel        text,
    order_status   text,
    total_amount   numeric,
    kafka_partition int,
    kafka_offset   bigint,
    ingested_at    timestamptz DEFAULT now()
);

CREATE TABLE IF NOT EXISTS {config.STREAM_SCHEMA}.{config.ORDER_ITEMS_TABLE} (
    event_id       text,
    order_item_id  bigint,
    order_id       bigint,
    product_id     bigint,
    quantity       int,
    unit_price     numeric,
    discount_pct   numeric,
    price_paid     numeric,
    line_total     numeric,
    ingested_at    timestamptz DEFAULT now()
);
"""

INSERT_ORDER = text(f"""
INSERT INTO {config.STREAM_SCHEMA}.{config.ORDERS_TABLE}
    (event_id, order_id, customer_id, store_id, order_date, channel,
     order_status, total_amount, kafka_partition, kafka_offset)
VALUES
    (:event_id, :order_id, :customer_id, :store_id, :order_date, :channel,
     :order_status, :total_amount, :kafka_partition, :kafka_offset)
""")

INSERT_ITEM = text(f"""
INSERT INTO {config.STREAM_SCHEMA}.{config.ORDER_ITEMS_TABLE}
    (event_id, order_item_id, order_id, product_id, quantity,
     unit_price, discount_pct, price_paid, line_total)
VALUES
    (:event_id, :order_item_id, :order_id, :product_id, :quantity,
     :unit_price, :discount_pct, :price_paid, :line_total)
""")


def connect_db(retries=30, delay=2):
    for i in range(retries):
        try:
            engine = create_engine(config.DATABASE_URL)
            with engine.begin() as conn:
                conn.execute(text(DDL))
            log.info("connected to Postgres; %s schema ready", config.STREAM_SCHEMA)
            return engine
        except Exception as e:
            log.info("waiting for Postgres (%s/%s): %s", i + 1, retries, e)
            time.sleep(delay)
    raise RuntimeError("Postgres not reachable")


def write_event(engine, event, msg):
    order = event["order"]
    with engine.begin() as conn:
        conn.execute(INSERT_ORDER, {
            "event_id": event["event_id"],
            "order_id": order["order_id"],
            "customer_id": order["customer_id"],
            "store_id": order["store_id"],
            "order_date": order["order_date"],
            "channel": order["channel"],
            "order_status": order["order_status"],
            "total_amount": order["total_amount"],
            "kafka_partition": msg.partition(),
            "kafka_offset": msg.offset(),
        })
        for it in event["items"]:
            conn.execute(INSERT_ITEM, {"event_id": event["event_id"], "order_id": order["order_id"], **it})


def main():
    engine = connect_db()

    consumer = Consumer({
        "bootstrap.servers": config.KAFKA_BOOTSTRAP_SERVERS,
        "group.id": config.CONSUMER_GROUP_ID,
        "auto.offset.reset": "earliest",
        "enable.auto.commit": False,  # commit manually after the DB write
    })
    consumer.subscribe([config.ORDERS_TOPIC])
    log.info("subscribed to '%s'; waiting for messages...", config.ORDERS_TOPIC)

    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                log.warning("consume error: %s", msg.error())
                continue

            try:
                event = json.loads(msg.value())
                write_event(engine, event, msg)
                consumer.commit(message=msg)  # only after a successful write
                log.info(
                    "landed order_id=%s (%d items) [p%d@%d]",
                    event["order"]["order_id"], len(event["items"]),
                    msg.partition(), msg.offset(),
                )
            except Exception as e:
                # Do NOT commit: the message will be redelivered and retried.
                log.warning("failed to process offset %d: %s", msg.offset(), e)
                time.sleep(1)
    finally:
        consumer.close()
        engine.dispose()


if __name__ == "__main__":
    main()
