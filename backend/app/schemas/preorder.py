from datetime import date
from uuid import UUID
from pydantic import BaseModel, Field
from typing import Optional

class PreorderItemCreate(BaseModel):
    menu_item_id: UUID
    quantity: int = Field(gt=0)

class PreorderCreate(BaseModel):
    business_id: UUID
    service_date: date
    slot_type: str
    fulfillment_mode: str
    customer_notes: Optional[str] = None
    items: list[PreorderItemCreate]
