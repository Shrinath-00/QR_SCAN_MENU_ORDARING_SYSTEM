from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class InvoiceCreate(BaseModel):
    order_id: str
    payment_method: Optional[str] = "CASH"

class InvoiceResponse(BaseModel):
    id: int
    invoice_id: str
    order_id: str
    total_amount: float
    payment_method: str
    payment_status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
