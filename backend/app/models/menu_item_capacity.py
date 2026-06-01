import uuid
from datetime import date
from sqlalchemy import String, Integer, Date, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class MenuItemCapacity(Base):
    __tablename__ = "menu_item_capacities"
    __table_args__ = (UniqueConstraint("menu_item_id", "service_date", "slot_type", name="uq_menu_item_capacity"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    menu_item_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("menu_items.id", ondelete="CASCADE"), nullable=False)
    service_date: Mapped[date] = mapped_column(Date, nullable=False)
    slot_type: Mapped[str] = mapped_column(String(20), nullable=False)
    total_capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    reserved_capacity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    remaining_capacity: Mapped[int] = mapped_column(Integer, nullable=False)
