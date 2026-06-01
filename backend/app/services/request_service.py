from datetime import date
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.custom_request import CustomRequest
from app.schemas.custom_request import CustomRequestCreate


def create_request(db: Session, user_id: str, payload: CustomRequestCreate) -> CustomRequest:
    if payload.target_date <= date.today():
        raise HTTPException(status_code=400, detail="Request date must be in the future")
    request = CustomRequest(user_id=user_id, status="open", **payload.model_dump())
    db.add(request)
    db.commit()
    db.refresh(request)
    return request
