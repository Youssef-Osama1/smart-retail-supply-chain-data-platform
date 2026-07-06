import os

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")

ORDERS_TOPIC = os.getenv("KAFKA_ORDERS_TOPIC", "orders")
ORDERS_TOPIC_PARTITIONS = int(os.getenv("KAFKA_ORDERS_PARTITIONS", "3"))
ORDERS_TOPIC_REPLICATION = int(os.getenv("KAFKA_ORDERS_REPLICATION", "1"))

CONSUMER_GROUP_ID = os.getenv("KAFKA_CONSUMER_GROUP", "bronze-stream-loader")


ORDERS_PER_SECOND = float(os.getenv("STREAM_ORDERS_PER_SECOND", "2"))


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://airflow:airflow@postgres:5432/retail",
)

STREAM_SCHEMA = os.getenv("STREAM_SCHEMA", "bronze_stream")
ORDERS_TABLE = "orders_raw"
ORDER_ITEMS_TABLE = "order_items_raw"
