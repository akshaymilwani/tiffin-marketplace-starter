from uuid import UUID
from pydantic import BaseModel, Field
from typing import Optional

class BusinessCreate(BaseModel):
    business_name: str = Field(min_length=2, max_length=200)
    description: Optional[str] = None
    cuisine_type: str
    pickup_enabled: bool = True
    self_delivery_enabled: bool = False
    service_radius_km: Optional[float] = None
    minimum_order_for_delivery: Optional[float] = None
    flat_delivery_fee: float = 0
    service_zone_text: Optional[str] = None
    address_line1: str
    address_line2: Optional[str] = None
    city: str
    province: str
    postal_code: str

class BusinessResponse(BaseModel):
    id: UUID
    business_name: str
    slug: str
    cuisine_type: str
    city: str
    province: str
    verification_status: str
    public_listing_status: str
    avg_rating: float | None = None
    total_reviews: int = 0

    class Config:
        from_attributes = True
