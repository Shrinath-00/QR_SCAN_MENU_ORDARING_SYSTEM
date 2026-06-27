from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.database import Base

class Invoice(Base):
    __tablename__ = "invoices"
    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(String(50), unique=True, index=True, nullable=False)
    order_id = Column(String(50), ForeignKey("orders.order_id"), nullable=False)
    total_amount = Column(Float, nullable=False)
    payment_method = Column(String(50), default="CASH", nullable=False)
    payment_status = Column(String(20), default="PAID", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    order = relationship("Order")
