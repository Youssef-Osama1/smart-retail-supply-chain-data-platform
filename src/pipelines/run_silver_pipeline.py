import sys
from pathlib import Path

# Add project root to PYTHONPATH
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))

SILVER = Path("data/04_silver")
SILVER.mkdir(parents=True, exist_ok=True)


from src.Silver.clean_products import clean_products
from src.Silver.clean_customers import clean_customers
from src.Silver.clean_stores import clean_stores
from src.Silver.clean_warehouses import clean_warehouses
from src.Silver.clean_orders import clean_orders
from src.Silver.clean_order_items import clean_order_items
from src.Silver.clean_store_inventory import clean_store_inventory
from src.Silver.clean_warehouse_inventory import clean_warehouse_inventory
from src.Silver.clean_shipments import clean_shipments
from src.Silver.clean_shipment_items import clean_shipment_items


def run_silver_pipeline():
    clean_products()
    clean_customers()
    clean_stores()
    clean_warehouses()
    clean_orders()
    clean_order_items()
    clean_store_inventory()
    clean_warehouse_inventory()
    clean_shipments()
    clean_shipment_items()
    print("\nSilver Pipeline Completed Successfully")


if __name__ == "__main__":
    run_silver_pipeline()