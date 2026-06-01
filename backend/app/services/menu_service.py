from sqlalchemy.orm import Session
from app.models.menu_item import MenuItem
from app.schemas.menu_item import MenuItemCreate


def create_menu_item(db: Session, payload: MenuItemCreate) -> MenuItem:
    item = MenuItem(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def list_business_menu(db: Session, business_id: str):
    return db.query(MenuItem).filter(MenuItem.business_id == business_id, MenuItem.is_active.is_(True)).all()
