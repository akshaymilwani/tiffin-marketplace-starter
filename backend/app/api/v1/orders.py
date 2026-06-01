from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import db_dep, get_mock_user_id
from app.schemas.preorder import PreorderCreate
from app.services.order_service import create_preorder

router = APIRouter()

@router.post("")
def create_order(payload: PreorderCreate, db: Session = Depends(db_dep), user_id: str = Depends(get_mock_user_id)):
    return create_preorder(db, user_id, payload)
