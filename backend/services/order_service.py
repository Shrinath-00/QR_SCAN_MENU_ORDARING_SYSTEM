from sqlalchemy.orm import Session
from fastapi import HTTPException, WebSocket
from typing import List, Dict
import json
import logging
from backend.models.orders import Order
from backend.schemas.orders import OrderCreate, OrderUpdate
from backend.security import verify_qr_signature

logger = logging.getLogger("hotel_management")

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        payload = json.dumps(message, default=str)
        dead_connections = []
        for connection in self.active_connections:
            try:
                await connection.send_text(payload)
            except Exception:
                dead_connections.append(connection)

        for conn in dead_connections:
            self.disconnect(conn)

manager = ConnectionManager()

def create_order_service(db: Session, order_data: OrderCreate) -> Order:
    if not verify_qr_signature(order_data.table_id, order_data.sig):
        raise HTTPException(status_code=403, detail="Invalid QR code signature — table verification failed.")

    existing = db.query(Order).filter(
        Order.table_id == order_data.table_id,
        Order.status == "OPEN"
    ).first()

    if existing:
        current_items = [dict(i) for i in existing.items]

        for new_item in order_data.items:
            found = next((i for i in current_items if i["name"] == new_item.name), None)
            if found:
                found["qty"] += new_item.qty
            else:
                current_items.append(new_item.dict())

        existing.items = current_items
        if order_data.customer_phone:
            existing.customer_phone = order_data.customer_phone
        db.commit()
        db.refresh(existing)
        return existing
    else:
        new_order = Order(
            order_id=order_data.order_id,
            table_id=order_data.table_id,
            customer_phone=order_data.customer_phone,
            items=[i.dict() for i in order_data.items],
            status=order_data.status
        )
        db.add(new_order)
        db.commit()
        db.refresh(new_order)
        return new_order

def cleanup_old_history(db: Session):
    try:
        from datetime import datetime
        # Get today's local midnight as a timezone-aware datetime (system local time)
        local_now = datetime.now().astimezone()
        local_midnight = local_now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Query all orders created before local midnight today (yesterday's and older)
        old_orders = db.query(Order).filter(
            Order.created_at < local_midnight
        ).all()
        
        if old_orders:
            order_ids = [o.order_id for o in old_orders]
            
            # Delete corresponding invoices
            from backend.models.invoice import Invoice
            db.query(Invoice).filter(Invoice.order_id.in_(order_ids)).delete(synchronize_session=False)
            
            # Delete the orders
            db.query(Order).filter(Order.order_id.in_(order_ids)).delete(synchronize_session=False)
            
            db.commit()
            logger.info(f"Cleaned up {len(order_ids)} old orders and invoices from history (created before {local_midnight}).")
    except Exception as e:
        logger.error(f"Error during old history cleanup: {e}")
        db.rollback()

def get_orders_service(db: Session) -> List[Order]:
    cleanup_old_history(db)
    return db.query(Order).filter(
        Order.table_id != "N/A"
    ).order_by(Order.created_at.asc()).all()

def get_order_by_id_service(db: Session, order_id: str) -> Order:
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

def update_order_status_service(db: Session, order_id: str, update_data: OrderUpdate) -> Order:
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    order.status = update_data.status
    db.commit()
    db.refresh(order)
    return order
