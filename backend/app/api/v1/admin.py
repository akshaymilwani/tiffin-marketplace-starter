from datetime import date, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import db_dep, require_admin_user
from app.models.business import Business
from app.models.merchant_verification import MerchantVerification
from app.models.subscription import Subscription
from app.models.user import User

router = APIRouter()


class VerificationReview(BaseModel):
    decision: str
    rejection_reason: str | None = None


class BusinessReview(BaseModel):
    decision: str
    rejection_reason: str | None = None


class SubscriptionActivation(BaseModel):
    plan_tier: str = "basic"
    payment_type: str = "free"
    renewal_date: date | None = None
    notes: str | None = None


def _iso(value):
    return value.isoformat() if value else None


def _serialize_business(business: Business, subscription: Subscription | None = None) -> dict:
    return {
        "id": str(business.id),
        "business_name": business.business_name,
        "slug": business.slug,
        "cuisine_type": business.cuisine_type,
        "city": business.city,
        "province": business.province,
        "verification_status": business.verification_status,
        "public_listing_status": business.public_listing_status,
        "subscription_status": subscription.status if subscription else "inactive",
        "plan_tier": subscription.plan_tier if subscription else "",
        "payment_type": subscription.payment_type if subscription else "free",
        "created_at": _iso(business.created_at),
    }


def _serialize_verification(verification: MerchantVerification, business: Business) -> dict:
    return {
        "id": str(verification.id),
        "business_id": str(verification.business_id),
        "business_name": business.business_name,
        "cert_number": verification.cert_number,
        "issuing_authority": verification.issuing_authority,
        "cert_file_url": verification.cert_file_url,
        "address_proof_file_url": verification.address_proof_file_url,
        "decision": verification.decision,
        "rejection_reason": verification.rejection_reason,
        "submitted_at": _iso(verification.submitted_at),
        "reviewed_at": _iso(verification.reviewed_at),
    }


@router.get("/dashboard")
def admin_dashboard(db: Session = Depends(db_dep), admin_user: User = Depends(require_admin_user)):
    pending_verifications = db.query(MerchantVerification).filter(MerchantVerification.decision == "pending").count()
    active_merchants = db.query(Business).filter(Business.public_listing_status == "visible").count()
    expired_subscriptions = db.query(Subscription).filter(Subscription.status == "expired").count()
    return {
        "pending_verifications": pending_verifications,
        "active_merchants": active_merchants,
        "expired_subscriptions": expired_subscriptions,
    }


@router.get("/businesses")
def list_businesses(db: Session = Depends(db_dep), admin_user: User = Depends(require_admin_user)):
    businesses = db.query(Business).order_by(Business.created_at.desc()).all()
    results = []
    for business in businesses:
        subscription = (
            db.query(Subscription)
            .filter(Subscription.business_id == business.id)
            .order_by(Subscription.created_at.desc())
            .first()
        )
        results.append(_serialize_business(business, subscription))
    return results


@router.get("/verifications")
def list_verifications(
    status: str | None = None,
    db: Session = Depends(db_dep),
    admin_user: User = Depends(require_admin_user),
):
    query = db.query(MerchantVerification, Business).join(Business, MerchantVerification.business_id == Business.id)
    if status:
        query = query.filter(MerchantVerification.decision == status)
    rows = query.order_by(MerchantVerification.submitted_at.desc()).all()
    return [_serialize_verification(verification, business) for verification, business in rows]


@router.put("/verifications/{verification_id}/review")
def review_verification(
    verification_id: UUID,
    payload: VerificationReview,
    db: Session = Depends(db_dep),
    admin_user: User = Depends(require_admin_user),
):
    if payload.decision not in {"approved", "rejected", "pending"}:
        raise HTTPException(status_code=400, detail="Decision must be approved, rejected, or pending")

    verification = db.query(MerchantVerification).filter(MerchantVerification.id == verification_id).first()
    if not verification:
        raise HTTPException(status_code=404, detail="Verification not found")
    business = db.query(Business).filter(Business.id == verification.business_id).first()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")

    verification.decision = payload.decision
    verification.rejection_reason = payload.rejection_reason if payload.decision == "rejected" else None
    verification.reviewed_at = datetime.utcnow()
    verification.reviewed_by = admin_user.id
    verification.badge_issued_at = datetime.utcnow() if payload.decision == "approved" else None

    business.verification_status = payload.decision
    business.public_listing_status = "visible" if payload.decision == "approved" else "hidden"
    business.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(verification)
    return _serialize_verification(verification, business)


@router.put("/businesses/{business_id}/review")
def review_business(
    business_id: UUID,
    payload: BusinessReview,
    db: Session = Depends(db_dep),
    admin_user: User = Depends(require_admin_user),
):
    if payload.decision not in {"approved", "rejected", "pending"}:
        raise HTTPException(status_code=400, detail="Decision must be approved, rejected, or pending")

    business = db.query(Business).filter(Business.id == business_id).first()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")

    business.verification_status = payload.decision
    business.public_listing_status = "visible" if payload.decision == "approved" else "hidden"
    business.updated_at = datetime.utcnow()

    verification = (
        db.query(MerchantVerification)
        .filter(MerchantVerification.business_id == business.id)
        .order_by(MerchantVerification.submitted_at.desc())
        .first()
    )
    if verification:
        verification.decision = payload.decision
        verification.rejection_reason = payload.rejection_reason if payload.decision == "rejected" else None
        verification.reviewed_at = datetime.utcnow()
        verification.reviewed_by = admin_user.id
        verification.badge_issued_at = datetime.utcnow() if payload.decision == "approved" else None

    db.commit()
    db.refresh(business)
    return _serialize_business(business)


@router.post("/businesses/{business_id}/subscription")
def activate_subscription(
    business_id: UUID,
    payload: SubscriptionActivation,
    db: Session = Depends(db_dep),
    admin_user: User = Depends(require_admin_user),
):
    business = db.query(Business).filter(Business.id == business_id).first()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    if payload.payment_type not in {"free", "paid"}:
        raise HTTPException(status_code=400, detail="Payment type must be free or paid")

    existing = db.query(Subscription).filter(Subscription.business_id == business.id, Subscription.status == "active").all()
    for subscription in existing:
        subscription.status = "inactive"
        subscription.end_date = date.today()
        subscription.updated_at = datetime.utcnow()

    subscription = Subscription(
        business_id=business.id,
        plan_tier=payload.plan_tier,
        payment_type=payload.payment_type,
        status="active",
        activated_by=admin_user.id,
        start_date=date.today(),
        renewal_date=payload.renewal_date,
        notes=payload.notes,
    )
    db.add(subscription)
    db.commit()
    db.refresh(subscription)
    return {
        "id": str(subscription.id),
        "business_id": str(subscription.business_id),
        "plan_tier": subscription.plan_tier,
        "payment_type": subscription.payment_type,
        "status": subscription.status,
        "start_date": _iso(subscription.start_date),
        "renewal_date": _iso(subscription.renewal_date),
        "notes": subscription.notes,
    }
