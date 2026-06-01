import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Text, Numeric, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

class Business(Base):
    __tablename__ = "businesses"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    business_name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    cuisine_type: Mapped[str] = mapped_column(String(100), nullable=False)
    pickup_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    self_delivery_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    service_radius_km: Mapped[float | None] = mapped_column(Numeric(5, 2))
    minimum_order_for_delivery: Mapped[float | None] = mapped_column(Numeric(10, 2))
    flat_delivery_fee: Mapped[float | None] = mapped_column(Numeric(10, 2), default=0)
    service_zone_text: Mapped[str | None] = mapped_column(Text)
    address_line1: Mapped[str] = mapped_column(Text, nullable=False)
    address_line2: Mapped[str | None] = mapped_column(Text)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    province: Mapped[str] = mapped_column(String(50), nullable=False)
    postal_code: Mapped[str] = mapped_column(String(20), nullable=False)
    verification_status: Mapped[str] = mapped_column(String(30), default="pending", nullable=False)
    public_listing_status: Mapped[str] = mapped_column(String(30), default="hidden", nullable=False)
    trust_score: Mapped[float | None] = mapped_column(Numeric(5, 2), default=0)
    avg_rating: Mapped[float | None] = mapped_column(Numeric(3, 2), default=0)
    total_reviews: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    cancellation_rate: Mapped[float | None] = mapped_column(Numeric(5, 2), default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    owner = relationship("User", back_populates="businesses")
    menu_items = relationship("MenuItem", back_populates="business", cascade="all, delete-orphan")
