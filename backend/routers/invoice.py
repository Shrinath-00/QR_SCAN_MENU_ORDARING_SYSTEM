from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.schemas.invoice import InvoiceCreate, InvoiceResponse
from backend.services.invoice_service import (
    generate_invoice_service,
    get_invoice_by_id_service,
    get_invoice_by_order_id_service
)
from backend.routers.auth import RoleChecker

router = APIRouter(prefix="/api/invoices", tags=["Invoice Management"])

@router.post("", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
def generate_invoice(
    invoice_data: InvoiceCreate,
    db: Session = Depends(get_db),
    current_user = Depends(RoleChecker(["admin", "waiter"]))
):
    return generate_invoice_service(db, invoice_data)

@router.get("/{invoice_id}", response_model=InvoiceResponse)
def get_invoice_by_id(invoice_id: str, db: Session = Depends(get_db)):
    return get_invoice_by_id_service(db, invoice_id)

@router.get("/order/{order_id}", response_model=InvoiceResponse)
def get_invoice_by_order_id(order_id: str, db: Session = Depends(get_db)):
    return get_invoice_by_order_id_service(db, order_id)
