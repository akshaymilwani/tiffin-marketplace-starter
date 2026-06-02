from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, selectinload

from app.api.deps import db_dep, get_mock_user_id
from app.models.preorder import Preorder
from app.schemas.preorder import PreorderCreate
from app.services.order_service import create_preorder

router = APIRouter()


def _money(value):
    return float(value or 0)


def _iso(value):
    return value.isoformat() if value else None


def _serialize_order(order: Preorder) -> dict:
    return {
        "id": str(order.id),
        "order_number": order.order_number,
        "business_id": str(order.business_id),
        "service_date": _iso(order.service_date),
        "slot_type": order.slot_type,
        "source": order.source,
        "status": order.status,
        "fulfillment_mode": order.fulfillment_mode,
        "subtotal": _money(order.subtotal),
        "delivery_fee": _money(order.delivery_fee),
        "total_amount": _money(order.total_amount),
        "payment_mode": order.payment_mode,
        "customer_notes": order.customer_notes,
        "merchant_notes": order.merchant_notes,
        "created_at": _iso(order.created_at),
        "accepted_at": _iso(order.accepted_at),
        "rejected_at": _iso(order.rejected_at),
        "fulfilled_at": _iso(order.fulfilled_at),
        "items": [
            {
                "id": str(item.id),
                "menu_item_id": str(item.menu_item_id),
                "name": item.item_name_snapshot,
                "unit_price": _money(item.unit_price),
                "quantity": item.quantity,
                "line_total": _money(item.line_total),
            }
            for item in order.items
        ],
    }


@router.post("")
def create_order(payload: PreorderCreate, db: Session = Depends(db_dep), user_id: str = Depends(get_mock_user_id)):
    return create_preorder(db, user_id, payload)


@router.get("")
def list_my_orders(db: Session = Depends(db_dep), user_id: str = Depends(get_mock_user_id)):
    orders = (
        db.query(Preorder)
        .options(selectinload(Preorder.items))
        .filter(Preorder.user_id == user_id)
        .order_by(Preorder.created_at.desc())
        .all()
    )
    return [_serialize_order(order) for order in orders]
