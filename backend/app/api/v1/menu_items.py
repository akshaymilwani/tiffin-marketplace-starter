from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import db_dep
from app.schemas.menu_item import MenuItemCreate, MenuItemResponse
from app.services.menu_service import create_menu_item

router = APIRouter()

@router.post("", response_model=MenuItemResponse)
def create_menu_item_route(payload: MenuItemCreate, db: Session = Depends(db_dep)):
    return create_menu_item(db, payload)
