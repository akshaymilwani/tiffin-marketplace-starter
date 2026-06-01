from datetime import datetime, timedelta
from uuid import uuid4
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.business import Business
from app.models.menu_item import MenuItem
from app.models.preorder import Preorder
from app.models.preorder_item import PreorderItem
from app.schemas.preorder import PreorderCreate
from app.services.capacity_service import reserve_slot_capacity


def create_preorder(db: Session, user_id: str, payload: PreorderCreate) -> Preorder:
    business = db.query(Business).filter(Business.id == payload.business_id).first()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    if business.public_listing_status != "visible":
        raise HTTPException(status_code=400, detail="Business is not available for ordering")

    menu_items = db.query(MenuItem).filter(MenuItem.id.in_([i.menu_item_id for i in payload.items])).all()
    menu_map = {str(item.id): item for item in menu_items}
    if len(menu_items) != len(payload.items):
        raise HTTPException(status_code=400, detail="One or more menu items are invalid")

    total_qty = sum(i.quantity for i in payload.items)
    reserve_slot_capacity(db, str(payload.business_id), payload.service_date, payload.slot_type, total_qty)

    subtotal = 0.0
    order = Preorder(
        order_number=f"ORD-{uuid4().hex[:10].upper()}",
        user_id=user_id,
        business_id=payload.business_id,
        service_date=payload.service_date,
        slot_type=payload.slot_type,
        source="direct",
        status="pending",
        fulfillment_mode=payload.fulfillment_mode,
        customer_notes=payload.customer_notes,
        expires_at=datetime.utcnow() + timedelta(hours=2),
    )
    db.add(order)
    db.flush()

    for requested_item in payload.items:
        item = menu_map[str(requested_item.menu_item_id)]
        line_total = float(item.price) * requested_item.quantity
        subtotal += line_total
        db.add(
            PreorderItem(
                preorder_id=order.id,
                menu_item_id=item.id,
                item_name_snapshot=item.name,
                unit_price=item.price,
                quantity=requested_item.quantity,
                line_total=line_total,
            )
        )

    order.subtotal = subtotal
    order.delivery_fee = float(business.flat_delivery_fee or 0) if payload.fulfillment_mode == "self_delivery" else 0
    order.total_amount = float(order.subtotal) + float(order.delivery_fee)

    db.commit()
    db.refresh(order)
    return order
