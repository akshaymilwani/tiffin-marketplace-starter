from uuid import UUID
from pydantic import BaseModel
from typing import Optional

class MenuItemCreate(BaseModel):
    business_id: UUID
    name: str
    description: Optional[str] = None
    price: float
    cuisine_tag: Optional[str] = None
    dietary_tags: list[str] = []
    spice_level: Optional[str] = None
    prep_lead_time_hours: int = 0
    available_days: list[str] = []
    available_slots: list[str] = []

class MenuItemResponse(BaseModel):
    id: UUID
    name: str
    price: float
    is_active: bool

    class Config:
        from_attributes = True
