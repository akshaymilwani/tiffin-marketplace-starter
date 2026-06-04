from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import db_dep, get_mock_user_id
from app.models.business import Business
from app.models.preorder import Preorder
from app.models.review import Review

router = APIRouter()


class ReviewSubmit(BaseModel):
    preorder_id: UUID
    rating: int = Field(ge=1, le=5)
    review_text: str | None = None


def _serialize_review(review: Review) -> dict:
    return {
        "id": str(review.id),
        "preorder_id": str(review.preorder_id),
        "business_id": str(review.business_id),
        "user_id": str(review.user_id),
        "rating": review.rating,
        "review_text": review.review_text,
        "created_at": review.created_at.isoformat() if review.created_at else None,
    }


def _refresh_business_rating(db: Session, business_id: UUID) -> None:
    rating_summary = (
        db.query(func.avg(Review.rating).label("avg_rating"), func.count(Review.id).label("total_reviews"))
        .filter(Review.business_id == business_id)
        .one()
    )
    business = db.query(Business).filter(Business.id == business_id).first()
    if business:
        business.avg_rating = rating_summary.avg_rating or 0
        business.total_reviews = int(rating_summary.total_reviews or 0)
        business.updated_at = datetime.utcnow()


@router.post("")
def submit_review(payload: ReviewSubmit, db: Session = Depends(db_dep), user_id: str = Depends(get_mock_user_id)):
    order = db.query(Preorder).filter(Preorder.id == payload.preorder_id, Preorder.user_id == user_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.status != "fulfilled":
        raise HTTPException(status_code=400, detail="Only fulfilled orders can be reviewed")

    review = db.query(Review).filter(Review.preorder_id == order.id).first()
    if review:
        review.rating = payload.rating
        review.review_text = payload.review_text
    else:
        review = Review(
            preorder_id=order.id,
            business_id=order.business_id,
            user_id=order.user_id,
            rating=payload.rating,
            review_text=payload.review_text,
        )
        db.add(review)

    db.flush()
    _refresh_business_rating(db, order.business_id)
    db.commit()
    db.refresh(review)
    return _serialize_review(review)
