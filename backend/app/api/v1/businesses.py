from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import db_dep, get_mock_user_id
from app.schemas.business import BusinessCreate, BusinessResponse
from app.services.business_service import create_business, list_public_businesses, get_business_by_slug
from app.services.menu_service import list_business_menu

router = APIRouter()

@router.get("", response_model=list[BusinessResponse])
def list_businesses(db: Session = Depends(db_dep)):
    return list_public_businesses(db)


@router.post("", response_model=BusinessResponse)
def create_business_route(payload: BusinessCreate, db: Session = Depends(db_dep), user_id: str = Depends(get_mock_user_id)):
    return create_business(db, user_id, payload)


@router.get("/{business_id}/menu")
def get_business_menu_route(
    business_id: UUID,
    db: Session = Depends(db_dep),
):
    return list_business_menu(db, str(business_id))


@router.get("/{slug}")
def get_business(slug: str, db: Session = Depends(db_dep)):
    business = get_business_by_slug(db, slug)
    menu = list_business_menu(db, str(business.id))
    return {"business": business, "menu": menu}