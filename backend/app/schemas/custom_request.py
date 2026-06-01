from datetime import date
from pydantic import BaseModel
from typing import Optional

class CustomRequestCreate(BaseModel):
    title: str
    description: Optional[str] = None
    cuisine_tag: str
    quantity: int
    target_date: date
    budget_min: Optional[float] = None
    budget_max: Optional[float] = None
    location_text: str
    dietary_notes: Optional[str] = None
