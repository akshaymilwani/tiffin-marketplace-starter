from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import db_dep, get_mock_user_id
from app.schemas.custom_request import CustomRequestCreate
from app.services.request_service import create_request

router = APIRouter()

@router.post("")
def create_request_route(payload: CustomRequestCreate, db: Session = Depends(db_dep), user_id: str = Depends(get_mock_user_id)):
    return create_request(db, user_id, payload)
