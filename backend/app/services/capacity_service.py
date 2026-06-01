from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.slot_capacity import SlotCapacity


def reserve_slot_capacity(db: Session, business_id: str, service_date, slot_type: str, quantity: int) -> None:
    stmt = (
        select(SlotCapacity)
        .where(
            SlotCapacity.business_id == business_id,
            SlotCapacity.service_date == service_date,
            SlotCapacity.slot_type == slot_type,
        )
        .with_for_update()
    )
    slot = db.execute(stmt).scalar_one_or_none()
    if not slot:
        raise HTTPException(status_code=400, detail="Slot capacity not configured")
    if slot.is_closed or slot.remaining_capacity < quantity:
        raise HTTPException(status_code=400, detail="Selected slot is sold out")

    slot.reserved_capacity += quantity
    slot.remaining_capacity -= quantity
