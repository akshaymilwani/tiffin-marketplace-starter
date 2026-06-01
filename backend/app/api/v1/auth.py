from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import db_dep
from app.schemas.auth import SignUpRequest, LoginRequest
from app.services.auth_service import signup, login

router = APIRouter()

@router.post("/signup")
def signup_route(payload: SignUpRequest, db: Session = Depends(db_dep)):
    return signup(db, payload)

@router.post("/login")
def login_route(payload: LoginRequest, db: Session = Depends(db_dep)):
    return login(db, payload)
