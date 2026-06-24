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
from src.Silver.clean_returns import clean_returns
from src.Silver.clean_promotions import clean_promotions


def run_silver_pipeline():
    # Order matters: dimensions first, then facts that reference them.
    clean_products()
    clean_customers()
    clean_stores()
    clean_warehouses()
    clean_promotions()
    clean_orders()
    clean_order_items()        # needs products + orders
    clean_store_inventory()
    clean_warehouse_inventory()
    clean_shipments()          # needs orders
    clean_shipment_items()     # needs products + shipments
    clean_returns()            # needs order_items
    print("\nSilver Pipeline Completed Successfully")


if __name__ == "__main__":
    run_silver_pipeline()
