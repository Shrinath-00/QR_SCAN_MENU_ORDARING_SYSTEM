from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from backend.database import get_db
from backend.schemas.orders import OrderCreate, OrderUpdate, OrderResponse
from backend.services.order_service import (
    create_order_service,
    get_orders_service,
    get_order_by_id_service,
    update_order_status_service,
    manager
)
from backend.security import generate_qr_signature
from backend.routers.auth import RoleChecker

router = APIRouter(tags=["Order Management"])

@router.websocket("/ws/kitchen")
async def kitchen_websocket(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Wait for any incoming message to keep the socket alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@router.get("/api/qr-urls")
def get_qr_urls(base_url: str, total_tables: int = None, db: Session = Depends(get_db)):
    from backend.config import settings
    if total_tables is None:
        total_tables = settings.TOTAL_TABLES
    urls = []
    for i in range(1, total_tables + 1):
        sig = generate_qr_signature(str(i))
        urls.append({
            "table": i,
            "url": f"{base_url}/index.html?table={i}&sig={sig}"
        })
    return {"tables": urls}

@router.post("/api/orders", response_model=OrderResponse)
async def create_order(order_data: OrderCreate, db: Session = Depends(get_db)):

            
    from backend.models.orders import Order
    existing = db.query(Order).filter(
        Order.table_id == order_data.table_id,
        Order.status == "OPEN"
    ).first()
    
    order = create_order_service(db, order_data)
    
    event_type = "ORDER_UPDATED" if existing else "NEW_ORDER"
    await manager.broadcast({
        "type": event_type,
        "order": OrderResponse.model_validate(order).model_dump()
    })
    
    return order

@router.get("/api/orders", response_model=List[OrderResponse])
def get_orders(db: Session = Depends(get_db), current_user = Depends(RoleChecker(["admin", "waiter", "kitchen"]))):
    return get_orders_service(db)

@router.get("/api/orders/{order_id}", response_model=OrderResponse)
def get_order_by_id(order_id: str, db: Session = Depends(get_db)):
    # This endpoint is also called from the invoice page (which is public or waiter). 
    # To support public guest invoice viewing, we can allow it without auth, or check if user is admin/waiter.
    # Wait, the frontend invoice page fetches:
    # `fetch(`${CONFIG.API_URL}/api/orders/${orderId}`)`
    # without any auth headers! So this endpoint MUST be public or we must make sure invoice viewing doesn't crash.
    # The requirement says: "CRUD APIs for Menu Management, Order Management, Invoice Management". 
    # Let's keep `/api/orders/{order_id}` public so that guests can view their receipt/invoice, OR let's make it public.
    # Yes, public is better for invoice.html since it is accessed by customers as well as waiters.
    return get_order_by_id_service(db, order_id)

@router.patch("/api/orders/{order_id}", response_model=OrderResponse)
async def update_order_status(
    order_id: str,
    update_data: OrderUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(RoleChecker(["admin", "waiter", "kitchen"]))
):
    order = update_order_status_service(db, order_id, update_data)
    
    await manager.broadcast({
        "type": "STATUS_UPDATED",
        "order": OrderResponse.model_validate(order).model_dump()
    })
    
    return order
