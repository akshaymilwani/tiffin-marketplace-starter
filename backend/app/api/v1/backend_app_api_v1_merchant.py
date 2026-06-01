from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.business import Business

router = APIRouter()


def get_current_user_id(x_user_id: str | None = Header(default=None, alias="X-User-Id")) -> UUID:
    """
    Starter auth helper.

    The Streamlit app sends X-User-Id after login.
    Later, replace this with proper JWT/session auth.
    """
    if not x_user_id:
        raise HTTPException(status_code=401, detail="Missing X-User-Id header for starter auth")

    try:
        return UUID(x_user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid X-User-Id header")


@router.get("/my-business")
def get_my_business(
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
):
    """
    Return the logged-in merchant's first business.

    MVP assumption:
    - one merchant user owns one business.
    Later, return a list or add business switching.
    """
    business = (
        db.query(Business)
        .filter(Business.owner_user_id == current_user_id)
        .order_by(Business.created_at.desc())
        .first()
    )

    if not business:
        return {
            "business_found": False,
            "business": None,
        }

    return {
        "business_found": True,
        "business": {
            "id": str(business.id),
            "business_name": business.business_name,
            "slug": business.slug,
            "cuisine_type": business.cuisine_type,
            "verification_status": business.verification_status,
            "public_listing_status": business.public_listing_status,
        },
    }
