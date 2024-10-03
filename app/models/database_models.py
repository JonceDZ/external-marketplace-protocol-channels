from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Float
from datetime import datetime
from app.db.database import Base

class LogEntry(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    OperationId = Column(Integer, nullable=False) ############
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
    product_id = Column(Integer, nullable=False) ######################
    name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    price = Column(Float, nullable=True)
    inventory = Column(Integer, nullable=True)
    # Añade otros campos necesarios, como categorías, marcas, etc.