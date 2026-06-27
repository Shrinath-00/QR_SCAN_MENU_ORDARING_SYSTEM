from sqlalchemy import Column, Integer, String, JSON, DateTime
from sqlalchemy.sql import func
from backend.database import Base

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String(50), unique=True, index=True, nullable=False)
    table_id = Column(String(50), nullable=False)
    customer_phone = Column(String(20), nullable=True)
    items = Column(JSON, nullable=False)  # [{"name": "Item Name", "price": 10.0, "qty": 2}]
    status = Column(String(20), default="OPEN", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
