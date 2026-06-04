from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import db_dep, get_current_user
from app.models.user import User
from app.schemas.auth import SignUpRequest, LoginRequest, PasswordUpdateRequest
from app.services.auth_service import signup, login, update_password

router = APIRouter()

@router.post("/signup")
def signup_route(payload: SignUpRequest, db: Session = Depends(db_dep)):
    return signup(db, payload)

@router.post("/login")
def login_route(payload: LoginRequest, db: Session = Depends(db_dep)):
    return login(db, payload)


@router.post("/password")
def update_password_route(
    payload: PasswordUpdateRequest,
    db: Session = Depends(db_dep),
    current_user: User = Depends(get_current_user),
):
    return update_password(db, current_user, payload)
