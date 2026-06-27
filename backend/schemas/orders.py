from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime

class OrderItem(BaseModel):
    name: str
    price: float
    qty: int

class OrderCreate(BaseModel):
    order_id: str
    table_id: str
    sig: str
    customer_phone: Optional[str] = None
    items: List[OrderItem]
    status: str = "OPEN"

class OrderUpdate(BaseModel):
    status: str

class OrderResponse(BaseModel):
    id: int
    order_id: str
    table_id: str
    customer_phone: Optional[str] = None
    items: List[OrderItem]
    status: str
    created_at: Optional[datetime]
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
