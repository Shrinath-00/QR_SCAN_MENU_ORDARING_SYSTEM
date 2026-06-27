from sqlalchemy.orm import Session
from fastapi import HTTPException
import uuid
from backend.models.invoice import Invoice
from backend.models.orders import Order
from backend.schemas.invoice import InvoiceCreate

def generate_invoice_service(db: Session, invoice_data: InvoiceCreate) -> Invoice:
    order = db.query(Order).filter(Order.order_id == invoice_data.order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    existing_invoice = db.query(Invoice).filter(Invoice.order_id == invoice_data.order_id).first()
    if existing_invoice:
        return existing_invoice

    total = 0.0
    for item in order.items:
        total += item.get("price", 0.0) * item.get("qty", 0)

    invoice_id = f"INV-{uuid.uuid4().hex[:8].upper()}"

    new_invoice = Invoice(
        invoice_id=invoice_id,
        order_id=invoice_data.order_id,
        total_amount=total,
        payment_method=invoice_data.payment_method or "CASH",
        payment_status="PAID"
    )

    order.status = "PAID"

    db.add(new_invoice)
    db.commit()
    db.refresh(new_invoice)
    return new_invoice

def get_invoice_by_id_service(db: Session, invoice_id: str) -> Invoice:
    invoice = db.query(Invoice).filter(Invoice.invoice_id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice

def get_invoice_by_order_id_service(db: Session, order_id: str) -> Invoice:
    invoice = db.query(Invoice).filter(Invoice.order_id == order_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found for this order")
    return invoice
