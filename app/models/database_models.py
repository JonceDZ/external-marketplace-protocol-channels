from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Float, ForeignKey, JSON
from datetime import datetime
from sqlalchemy.orm import relationship
from app.db.database import Base

class LogEntry(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    OperationId = Column(Integer, nullable=False)
    Operation = Column(String, nullable=False)
    Direction = Column(String, nullable=False)
    ContentSource = Column(Text, nullable=True)
    ContentTranslated = Column(Text, nullable=True)
    ContentDestination = Column(Text, nullable=True)
    BusinessMessage = Column(Text, nullable=True)
    Status = Column(String, nullable=False)
    Timestamp = Column(DateTime, default=datetime.utcnow)

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    sku_id = Column(Integer, unique=True, index=True, nullable=False)
    product_id = Column(Integer, nullable=False)
    name = Column(String, nullable=False)
    product_description = Column(String, nullable=True)
    brand_name = Column(String, nullable=True)
    category_id = Column(Integer)
    category_name = Column(String)
    image_url = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    price = Column(Float, nullable=True)
    inventory = Column(Integer, nullable=True)


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String, unique=True, index=True, nullable=False)
    total_price = Column(Float, nullable=False)
    order_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="Pending")
    items = Column(JSON, nullable=False) 

class CartItem(Base):
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True, index=True)
    sku_id = Column(Integer, index=True, nullable=False)
    quantity = Column(Integer, nullable=False)
    sla_id = Column(String, nullable=True)
    sla_delivery_channel = Column(String, nullable=True)
    sla_list_price = Column(Float, nullable=True)
    sla_seller = Column(String, nullable=True)
    price = Column(Float, nullable=True)
    inventory = Column(Integer, nullable=True)
    user_id = Column(Integer, nullable=True)