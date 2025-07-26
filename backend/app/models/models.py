from sqlalchemy import Column, Integer, String, Float, DateTime
from app.services.database import Base

class DistributionCenter(Base):
    __tablename__ = 'distribution_centers'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
    latitude = Column(Float)
    longitude = Column(Float)

class InventoryItem(Base):
    __tablename__ = 'inventory_items'
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer)
    created_at = Column(DateTime)
    sold_at = Column(DateTime)
    cost = Column(Float)
    product_category = Column(String(255))
    product_name = Column(String(255))
    product_brand = Column(String(255))
    product_retail_price = Column(Float)
    product_department = Column(String(255))
    product_sku = Column(String(255))
    product_distribution_center_id = Column(Integer)

class OrderItem(Base):
    __tablename__ = 'order_items'
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer)
    user_id = Column(Integer)
    product_id = Column(Integer)
    inventory_item_id = Column(Integer)
    status = Column(String(255))
    created_at = Column(DateTime)
    shipped_at = Column(DateTime)
    delivered_at = Column(DateTime)
    returned_at = Column(DateTime)

class Order(Base):
    __tablename__ = 'orders'
    order_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    status = Column(String(255))
    gender = Column(String(50))
    created_at = Column(DateTime)
    returned_at = Column(DateTime)
    shipped_at = Column(DateTime)
    delivered_at = Column(DateTime)
    num_of_item = Column(Integer)

class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True, index=True)
    cost = Column(Float)
    category = Column(String(255))
    name = Column(String(255))
    brand = Column(String(255))
    retail_price = Column(Float)
    department = Column(String(255))
    sku = Column(String(255))
    distribution_center_id = Column(Integer)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(255))
    last_name = Column(String(255))
    email = Column(String(255))
    age = Column(Integer)
    gender = Column(String(50))
    state = Column(String(255))
    street_address = Column(String(255))
    postal_code = Column(String(50))
    city = Column(String(255))
    country = Column(String(255))
    latitude = Column(Float)
    longitude = Column(Float)
    traffic_source = Column(String(255))
    created_at = Column(DateTime)
