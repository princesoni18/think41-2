def query_orders_by_user_id(user_id: str):
    return list(db.orders.find({"user_id": int(user_id)}))

def query_product_by_id(product_id: str):
    return db.products.find_one({"id": int(product_id)})

def query_user_by_id(user_id: str):
    return db.users.find_one({"id": int(user_id)})

def query_inventory_item_by_id(item_id: str):
    return db.inventory_items.find_one({"id": int(item_id)})

def query_order_item_by_id(order_item_id: str):
    return db.order_items.find_one({"id": int(order_item_id)})
from app.services.database import db

def query_orders_by_order_id(order_id: str):
    return db.orders.find_one({"order_id": int(order_id)})

def query_products_by_name(name: str):
    return db.products.find_one({"name": name})

def query_user_by_email(email: str):
    return db.users.find_one({"email": email})

def query_inventory_by_product_id(product_id: str):
    return db.inventory_items.find_one({"product_id": int(product_id)})

def query_distribution_center_by_id(dc_id: str):
    return db.distribution_centers.find_one({"id": int(dc_id)})

def query_order_items_by_order_and_user(order_id: str, user_id: str):
    return list(db.order_items.find({"order_id": int(order_id), "user_id": int(user_id)}))
