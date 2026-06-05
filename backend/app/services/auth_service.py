from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime

from app.core.security import hash_password, verify_password, create_access_token
from app.models.user import User
from app.schemas.auth import SignUpRequest, LoginRequest, PasswordUpdateRequest


def signup(db: Session, payload: SignUpRequest):
    if payload.role not in {"customer", "merchant"}:
        raise HTTPException(status_code=400, detail="Public signup only supports customer or merchant accounts")

    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Unable to create account with these details")

    user = User(
        full_name=payload.full_name,
        email=payload.email,
        password_hash=hash_password(payload.password),
        role=payload.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"access_token": create_access_token(str(user.id)), "token_type": "bearer", "user_id": str(user.id), "role": user.role}


def login(db: Session, payload: LoginRequest):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not user.password_hash or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"access_token": create_access_token(str(user.id)), "token_type": "bearer", "user_id": str(user.id), "role": user.role}


def update_password(db: Session, user: User, payload: PasswordUpdateRequest):
    if not user.password_hash or not verify_password(payload.current_password, user.password_hash):
        raise HTTPException(status_code=401, detail="Current password is incorrect")
    if len(payload.new_password) < 6:
        raise HTTPException(status_code=400, detail="New password must be at least 6 characters")

    user.password_hash = hash_password(payload.new_password)
    user.updated_at = datetime.utcnow()
    db.commit()
    return {"message": "Password updated successfully"}
