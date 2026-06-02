from sqlalchemy.orm import Session
from slugify import slugify
from fastapi import HTTPException

from app.models.business import Business
from app.schemas.business import BusinessCreate


def create_business(db: Session, owner_user_id: str, payload: BusinessCreate) -> Business:
    existing_business = db.query(Business).filter(Business.owner_user_id == owner_user_id).first()
    if existing_business:
        raise HTTPException(
            status_code=400,
            detail="This merchant already has a business profile. Create a separate merchant login for another business.",
        )

    base_slug = slugify(payload.business_name)
    slug = base_slug
    index = 1
    while db.query(Business).filter(Business.slug == slug).first():
        index += 1
        slug = f"{base_slug}-{index}"

    business = Business(owner_user_id=owner_user_id, slug=slug, **payload.model_dump())
    db.add(business)
    db.commit()
    db.refresh(business)
    return business


def list_public_businesses(db: Session):
    return db.query(Business).filter(Business.public_listing_status == "visible").all()


def get_business_by_slug(db: Session, slug: str):
    business = db.query(Business).filter(Business.slug == slug).first()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    return business
