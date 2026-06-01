from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db


def db_dep(db: Session = Depends(get_db)) -> Session:
    return db


def get_mock_user_id(x_user_id: str | None = Header(default=None)) -> str:
    if not x_user_id:
        raise HTTPException(status_code=401, detail="Missing X-User-Id header for starter auth")
    return x_user_id
