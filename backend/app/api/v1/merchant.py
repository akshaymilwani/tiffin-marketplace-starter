from datetime import date, datetime, timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import extract, func
from sqlalchemy.orm import Session, selectinload

from app.api.deps import db_dep, get_mock_user_id
from app.models.business import Business
from app.models.custom_request import CustomRequest
from app.models.menu_item import MenuItem
from app.models.merchant_verification import MerchantVerification
from app.models.preorder import Preorder
from app.models.proposal import Proposal
from app.models.slot_capacity import SlotCapacity
from app.models.subscription import Subscription

router = APIRouter()


class OrderStatusUpdate(BaseModel):
    status: str
    merchant_notes: str | None = None


class SlotCapacityUpsert(BaseModel):
    service_date: date
    slot_type: str
    total_capacity: int = Field(gt=0)
    is_closed: bool = False


class BusinessProfileUpdate(BaseModel):
    business_name: str = Field(min_length=2, max_length=200)
    description: str | None = None
    cuisine_type: str
    pickup_enabled: bool = True
    self_delivery_enabled: bool = False
    service_radius_km: float | None = None
    minimum_order_for_delivery: float | None = None
    flat_delivery_fee: float = 0
    service_zone_text: str | None = None
    address_line1: str
    address_line2: str | None = None
    city: str
    province: str
    postal_code: str


class VerificationSubmit(BaseModel):
    cert_number: str | None = None
    issuing_authority: str | None = None
    cert_file_url: str | None = None
    address_proof_file_url: str | None = None


class ProposalSubmit(BaseModel):
    request_id: UUID
    quote_amount: float = Field(gt=0)
    eta_notes: str | None = None
    message: str | None = None


class MenuItemUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    price: float | None = Field(default=None, ge=0)
    cuisine_tag: str | None = None
    dietary_tags: list[str] | None = None
    spice_level: str | None = None
    prep_lead_time_hours: int | None = Field(default=None, ge=0)
    available_days: list[str] | None = None
    available_slots: list[str] | None = None
    is_active: bool | None = None


def _money(value):
    return float(value or 0)


def _iso(value):
    return value.isoformat() if value else None


def _business_for_user(db: Session, user_id: str) -> Business | None:
    return db.query(Business).filter(Business.owner_user_id == user_id).order_by(Business.created_at.desc()).first()


def _require_business(db: Session, user_id: str) -> Business:
    business = _business_for_user(db, user_id)
    if not business:
        raise HTTPException(status_code=404, detail="Business profile not found")
    return business


def _serialize_business(business: Business) -> dict:
    return {
        "id": str(business.id),
        "business_name": business.business_name,
        "slug": business.slug,
        "description": business.description,
        "cuisine_type": business.cuisine_type,
        "pickup_enabled": business.pickup_enabled,
        "self_delivery_enabled": business.self_delivery_enabled,
        "service_radius_km": _money(business.service_radius_km),
        "minimum_order_for_delivery": _money(business.minimum_order_for_delivery),
        "flat_delivery_fee": _money(business.flat_delivery_fee),
        "service_zone_text": business.service_zone_text,
        "address_line1": business.address_line1,
        "address_line2": business.address_line2,
        "city": business.city,
        "province": business.province,
        "postal_code": business.postal_code,
        "verification_status": business.verification_status,
        "public_listing_status": business.public_listing_status,
    }


def _serialize_menu_item(item: MenuItem) -> dict:
    return {
        "id": str(item.id),
        "business_id": str(item.business_id),
        "name": item.name,
        "description": item.description,
        "price": _money(item.price),
        "cuisine_tag": item.cuisine_tag,
        "dietary_tags": item.dietary_tags or [],
        "spice_level": item.spice_level,
        "is_active": item.is_active,
        "prep_lead_time_hours": item.prep_lead_time_hours,
        "available_days": item.available_days or [],
        "available_slots": item.available_slots or [],
    }


def _serialize_order(order: Preorder) -> dict:
    return {
        "id": str(order.id),
        "order_number": order.order_number,
        "user_id": str(order.user_id),
        "business_id": str(order.business_id),
        "service_date": _iso(order.service_date),
        "slot_type": order.slot_type,
        "source": order.source,
        "status": order.status,
        "fulfillment_mode": order.fulfillment_mode,
        "subtotal": _money(order.subtotal),
        "delivery_fee": _money(order.delivery_fee),
        "total_amount": _money(order.total_amount),
        "payment_mode": order.payment_mode,
        "customer_notes": order.customer_notes,
        "merchant_notes": order.merchant_notes,
        "created_at": _iso(order.created_at),
        "accepted_at": _iso(order.accepted_at),
        "rejected_at": _iso(order.rejected_at),
        "fulfilled_at": _iso(order.fulfilled_at),
        "items": [
            {
                "id": str(item.id),
                "menu_item_id": str(item.menu_item_id),
                "name": item.item_name_snapshot,
                "unit_price": _money(item.unit_price),
                "quantity": item.quantity,
                "line_total": _money(item.line_total),
            }
            for item in order.items
        ],
    }


@router.get("/dashboard")
def merchant_dashboard(
    month: int | None = None,
    months: str | None = None,
    year: int | None = None,
    service_date: date | None = None,
    db: Session = Depends(db_dep),
    user_id: str = Depends(get_mock_user_id),
):
    business = _require_business(db, user_id)
    today = date.today()
    selected_date = service_date or today
    next_date = selected_date + timedelta(days=1)
    selected_year = year or today.year
    selected_months: list[int] = []
    if months and months.lower() == "all":
        selected_months = []
    elif months:
        selected_months = [int(value) for value in months.split(",") if value.strip()]
    elif month:
        selected_months = [month]
    else:
        selected_months = [today.month]
    total_orders_for_date = db.query(Preorder).filter(Preorder.business_id == business.id, Preorder.service_date == selected_date).count()
    accepted_orders_for_date = (
        db.query(Preorder)
        .filter(Preorder.business_id == business.id, Preorder.service_date == selected_date, Preorder.status == "accepted")
        .count()
    )
    fulfilled_orders_for_date = (
        db.query(Preorder)
        .filter(Preorder.business_id == business.id, Preorder.service_date == selected_date, Preorder.status == "fulfilled")
        .count()
    )
    pending_orders_for_date = (
        db.query(Preorder)
        .filter(Preorder.business_id == business.id, Preorder.service_date == selected_date, Preorder.status == "pending")
        .count()
    )
    total_orders_next_day = (
        db.query(Preorder)
        .filter(Preorder.business_id == business.id, Preorder.service_date == next_date)
        .count()
    )
    open_requests = db.query(CustomRequest).filter(CustomRequest.status == "open").count()
    accepted_requests_today = (
        db.query(Proposal)
        .join(CustomRequest, Proposal.request_id == CustomRequest.id)
        .filter(
            Proposal.business_id == business.id,
            Proposal.status == "accepted",
            CustomRequest.target_date == selected_date,
        )
        .count()
    )
    accepted_requests_next_day = (
        db.query(Proposal)
        .join(CustomRequest, Proposal.request_id == CustomRequest.id)
        .filter(
            Proposal.business_id == business.id,
            Proposal.status == "accepted",
            CustomRequest.target_date == next_date,
        )
        .count()
    )
    fulfilled_requests_for_date = (
        db.query(Proposal)
        .join(CustomRequest, Proposal.request_id == CustomRequest.id)
        .filter(
            Proposal.business_id == business.id,
            Proposal.status == "fulfilled",
            CustomRequest.target_date == selected_date,
        )
        .count()
    )
    fulfilled_order_rows = (
        db.query(
            Preorder.service_date.label("service_date"),
            func.count(Preorder.id).label("fulfilled_orders"),
            func.coalesce(func.sum(Preorder.total_amount), 0).label("revenue"),
        )
        .filter(
            Preorder.business_id == business.id,
            Preorder.status == "fulfilled",
            extract("year", Preorder.service_date) == selected_year,
        )
    )
    if selected_months:
        fulfilled_order_rows = fulfilled_order_rows.filter(extract("month", Preorder.service_date).in_(selected_months))
    fulfilled_order_rows = fulfilled_order_rows.group_by(Preorder.service_date).order_by(Preorder.service_date.asc()).all()

    fulfilled_request_rows = (
        db.query(
            CustomRequest.target_date.label("service_date"),
            func.count(Proposal.id).label("fulfilled_requests"),
            func.coalesce(func.sum(Proposal.quote_amount), 0).label("revenue"),
        )
        .join(CustomRequest, Proposal.request_id == CustomRequest.id)
        .filter(
            Proposal.business_id == business.id,
            Proposal.status == "fulfilled",
            extract("year", CustomRequest.target_date) == selected_year,
        )
    )
    if selected_months:
        fulfilled_request_rows = fulfilled_request_rows.filter(extract("month", CustomRequest.target_date).in_(selected_months))
    fulfilled_request_rows = fulfilled_request_rows.group_by(CustomRequest.target_date).order_by(CustomRequest.target_date.asc()).all()

    daily_metrics_by_date = {}
    for row in fulfilled_order_rows:
        key = row.service_date
        daily_metrics_by_date[key] = {
            "date": _iso(row.service_date),
            "fulfilled_orders": int(row.fulfilled_orders or 0),
            "fulfilled_requests": 0,
            "orders": int(row.fulfilled_orders or 0),
            "revenue": _money(row.revenue),
        }
    for row in fulfilled_request_rows:
        key = row.service_date
        metrics = daily_metrics_by_date.setdefault(
            key,
            {
                "date": _iso(row.service_date),
                "fulfilled_orders": 0,
                "fulfilled_requests": 0,
                "orders": 0,
                "revenue": 0.0,
            },
        )
        fulfilled_requests = int(row.fulfilled_requests or 0)
        metrics["fulfilled_requests"] = fulfilled_requests
        metrics["orders"] += fulfilled_requests
        metrics["revenue"] += _money(row.revenue)

    subscription = (
        db.query(Subscription)
        .filter(Subscription.business_id == business.id)
        .order_by(Subscription.created_at.desc())
        .first()
    )
    return {
        "business": _serialize_business(business),
        "selected_date": _iso(selected_date),
        "next_date": _iso(next_date),
        "total_orders_for_date": total_orders_for_date,
        "accepted_orders_for_date": accepted_orders_for_date,
        "fulfilled_orders_for_date": fulfilled_orders_for_date,
        "pending_orders_for_date": pending_orders_for_date,
        "total_orders_next_day": total_orders_next_day,
        "total_orders_today": total_orders_for_date,
        "accepted_orders_today": accepted_orders_for_date,
        "fulfilled_orders_today": fulfilled_orders_for_date,
        "pending_orders_today": pending_orders_for_date,
        "total_orders_tomorrow": total_orders_next_day,
        "open_requests": open_requests,
        "accepted_requests_for_date": accepted_requests_today,
        "accepted_requests_next_day": accepted_requests_next_day,
        "fulfilled_requests_for_date": fulfilled_requests_for_date,
        "accepted_requests_today": accepted_requests_today,
        "accepted_requests_tomorrow": accepted_requests_next_day,
        "fulfilled_requests_today": fulfilled_requests_for_date,
        "daily_metrics": [daily_metrics_by_date[key] for key in sorted(daily_metrics_by_date)],
        "metrics_months": selected_months,
        "metrics_year": selected_year,
        "verification_status": business.verification_status,
        "subscription_status": subscription.status if subscription else "inactive",
    }


@router.get("/my-business")
def my_business(db: Session = Depends(db_dep), user_id: str = Depends(get_mock_user_id)):
    business = _business_for_user(db, user_id)
    return {"business_found": bool(business), "business": _serialize_business(business) if business else None}


@router.put("/my-business")
def update_my_business(payload: BusinessProfileUpdate, db: Session = Depends(db_dep), user_id: str = Depends(get_mock_user_id)):
    business = _require_business(db, user_id)
    for field, value in payload.model_dump().items():
        setattr(business, field, value)
    business.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(business)
    return _serialize_business(business)


@router.get("/menu-items")
def list_my_menu_items(db: Session = Depends(db_dep), user_id: str = Depends(get_mock_user_id)):
    business = _require_business(db, user_id)
    items = db.query(MenuItem).filter(MenuItem.business_id == business.id).order_by(MenuItem.created_at.desc()).all()
    return [_serialize_menu_item(item) for item in items]


@router.put("/menu-items/{item_id}")
def update_my_menu_item(
    item_id: UUID,
    payload: MenuItemUpdate,
    db: Session = Depends(db_dep),
    user_id: str = Depends(get_mock_user_id),
):
    business = _require_business(db, user_id)
    item = db.query(MenuItem).filter(MenuItem.id == item_id, MenuItem.business_id == business.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    item.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(item)
    return _serialize_menu_item(item)


@router.get("/capacity")
def list_capacity(db: Session = Depends(db_dep), user_id: str = Depends(get_mock_user_id)):
    business = _require_business(db, user_id)
    slots = (
        db.query(SlotCapacity)
        .filter(SlotCapacity.business_id == business.id)
        .order_by(SlotCapacity.service_date.asc(), SlotCapacity.slot_type.asc())
        .all()
    )
    return [
        {
            "id": str(slot.id),
            "service_date": _iso(slot.service_date),
            "slot_type": slot.slot_type,
            "total_capacity": slot.total_capacity,
            "reserved_capacity": slot.reserved_capacity,
            "remaining_capacity": slot.remaining_capacity,
            "is_closed": slot.is_closed,
        }
        for slot in slots
    ]


@router.post("/capacity")
def upsert_capacity(payload: SlotCapacityUpsert, db: Session = Depends(db_dep), user_id: str = Depends(get_mock_user_id)):
    business = _require_business(db, user_id)
    slot = (
        db.query(SlotCapacity)
        .filter(
            SlotCapacity.business_id == business.id,
            SlotCapacity.service_date == payload.service_date,
            SlotCapacity.slot_type == payload.slot_type,
        )
        .first()
    )
    if slot:
        if payload.total_capacity < slot.reserved_capacity:
            raise HTTPException(status_code=400, detail="Total capacity cannot be below already reserved capacity")
        slot.total_capacity = payload.total_capacity
        slot.remaining_capacity = payload.total_capacity - slot.reserved_capacity
        slot.is_closed = payload.is_closed
    else:
        slot = SlotCapacity(
            business_id=business.id,
            service_date=payload.service_date,
            slot_type=payload.slot_type,
            total_capacity=payload.total_capacity,
            reserved_capacity=0,
            remaining_capacity=payload.total_capacity,
            is_closed=payload.is_closed,
        )
        db.add(slot)
    db.commit()
    db.refresh(slot)
    return {"id": str(slot.id), "remaining_capacity": slot.remaining_capacity}


@router.get("/orders")
def list_orders(status: str | None = None, db: Session = Depends(db_dep), user_id: str = Depends(get_mock_user_id)):
    business = _require_business(db, user_id)
    query = db.query(Preorder).options(selectinload(Preorder.items)).filter(Preorder.business_id == business.id)
    if status:
        query = query.filter(Preorder.status == status)
    orders = query.order_by(Preorder.created_at.desc()).all()
    return [_serialize_order(order) for order in orders]


@router.put("/orders/{order_id}/status")
def update_order_status(
    order_id: UUID,
    payload: OrderStatusUpdate,
    db: Session = Depends(db_dep),
    user_id: str = Depends(get_mock_user_id),
):
    business = _require_business(db, user_id)
    order = db.query(Preorder).options(selectinload(Preorder.items)).filter(Preorder.id == order_id, Preorder.business_id == business.id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if payload.status not in {"pending", "accepted", "rejected", "fulfilled", "cancelled"}:
        raise HTTPException(status_code=400, detail="Unsupported order status")

    previous_status = order.status
    if payload.status in {"rejected", "cancelled"} and previous_status not in {"rejected", "cancelled"}:
        released_quantity = sum(item.quantity for item in order.items)
        slot = (
            db.query(SlotCapacity)
            .filter(
                SlotCapacity.business_id == business.id,
                SlotCapacity.service_date == order.service_date,
                SlotCapacity.slot_type == order.slot_type,
            )
            .first()
        )
        if slot:
            slot.reserved_capacity = max(0, slot.reserved_capacity - released_quantity)
            slot.remaining_capacity = min(slot.total_capacity, slot.remaining_capacity + released_quantity)

    order.status = payload.status
    order.merchant_notes = payload.merchant_notes
    order.updated_at = datetime.utcnow()
    if payload.status == "accepted":
        order.accepted_at = datetime.utcnow()
    elif payload.status == "rejected":
        order.rejected_at = datetime.utcnow()
    elif payload.status == "fulfilled":
        order.fulfilled_at = datetime.utcnow()

    db.commit()
    db.refresh(order)
    return _serialize_order(order)


@router.get("/verification")
def get_verification(db: Session = Depends(db_dep), user_id: str = Depends(get_mock_user_id)):
    business = _require_business(db, user_id)
    verification = (
        db.query(MerchantVerification)
        .filter(MerchantVerification.business_id == business.id)
        .order_by(MerchantVerification.submitted_at.desc())
        .first()
    )
    return {
        "business": _serialize_business(business),
        "verification": {
            "id": str(verification.id),
            "cert_number": verification.cert_number,
            "issuing_authority": verification.issuing_authority,
            "cert_file_url": verification.cert_file_url,
            "address_proof_file_url": verification.address_proof_file_url,
            "decision": verification.decision,
            "rejection_reason": verification.rejection_reason,
            "submitted_at": _iso(verification.submitted_at),
            "reviewed_at": _iso(verification.reviewed_at),
        }
        if verification
        else None,
    }


@router.post("/verification")
def submit_verification(payload: VerificationSubmit, db: Session = Depends(db_dep), user_id: str = Depends(get_mock_user_id)):
    business = _require_business(db, user_id)
    verification = MerchantVerification(business_id=business.id, decision="pending", **payload.model_dump())
    business.verification_status = "pending"
    db.add(verification)
    db.commit()
    db.refresh(verification)
    return {"id": str(verification.id), "decision": verification.decision}


@router.put("/verification")
def update_verification(payload: VerificationSubmit, db: Session = Depends(db_dep), user_id: str = Depends(get_mock_user_id)):
    business = _require_business(db, user_id)
    verification = (
        db.query(MerchantVerification)
        .filter(MerchantVerification.business_id == business.id)
        .order_by(MerchantVerification.submitted_at.desc())
        .first()
    )
    if not verification:
        verification = MerchantVerification(business_id=business.id, **payload.model_dump())
        db.add(verification)
    else:
        for field, value in payload.model_dump().items():
            setattr(verification, field, value)

    verification.decision = "pending"
    verification.rejection_reason = None
    verification.reviewed_at = None
    verification.reviewed_by = None
    verification.badge_issued_at = None
    business.verification_status = "pending"
    business.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(verification)
    return {"id": str(verification.id), "decision": verification.decision}


@router.get("/requests")
def list_open_requests(db: Session = Depends(db_dep), user_id: str = Depends(get_mock_user_id)):
    _require_business(db, user_id)
    requests = db.query(CustomRequest).filter(CustomRequest.status == "open").order_by(CustomRequest.created_at.desc()).all()
    return [
        {
            "id": str(request.id),
            "title": request.title,
            "description": request.description,
            "cuisine_tag": request.cuisine_tag,
            "quantity": request.quantity,
            "target_date": _iso(request.target_date),
            "budget_min": _money(request.budget_min),
            "budget_max": _money(request.budget_max),
            "location_text": request.location_text,
            "dietary_notes": request.dietary_notes,
            "status": request.status,
            "created_at": _iso(request.created_at),
        }
        for request in requests
    ]


@router.post("/proposals")
def submit_proposal(payload: ProposalSubmit, db: Session = Depends(db_dep), user_id: str = Depends(get_mock_user_id)):
    business = _require_business(db, user_id)
    request = db.query(CustomRequest).filter(CustomRequest.id == payload.request_id, CustomRequest.status == "open").first()
    if not request:
        raise HTTPException(status_code=404, detail="Open request not found")
    existing = db.query(Proposal).filter(Proposal.request_id == payload.request_id, Proposal.business_id == business.id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Proposal already submitted for this request")
    proposal = Proposal(business_id=business.id, status="submitted", **payload.model_dump())
    db.add(proposal)
    db.commit()
    db.refresh(proposal)
    return {"id": str(proposal.id), "status": proposal.status}


@router.get("/proposals")
def list_my_proposals(db: Session = Depends(db_dep), user_id: str = Depends(get_mock_user_id)):
    business = _require_business(db, user_id)
    rows = (
        db.query(Proposal, CustomRequest)
        .join(CustomRequest, Proposal.request_id == CustomRequest.id)
        .filter(Proposal.business_id == business.id)
        .order_by(Proposal.created_at.desc())
        .all()
    )
    return [
        {
            "id": str(proposal.id),
            "request_id": str(proposal.request_id),
            "request_title": request.title,
            "quote_amount": _money(proposal.quote_amount),
            "eta_notes": proposal.eta_notes,
            "message": proposal.message,
            "status": proposal.status,
            "created_at": _iso(proposal.created_at),
        }
        for proposal, request in rows
    ]


@router.get("/subscription")
def subscription_status(db: Session = Depends(db_dep), user_id: str = Depends(get_mock_user_id)):
    business = _require_business(db, user_id)
    subscription = (
        db.query(Subscription)
        .filter(Subscription.business_id == business.id)
        .order_by(Subscription.created_at.desc())
        .first()
    )
    return {
        "business": _serialize_business(business),
        "subscription": {
            "id": str(subscription.id),
            "plan_tier": subscription.plan_tier,
            "payment_type": subscription.payment_type,
            "status": subscription.status,
            "start_date": _iso(subscription.start_date),
            "renewal_date": _iso(subscription.renewal_date),
            "end_date": _iso(subscription.end_date),
            "notes": subscription.notes,
        }
        if subscription
        else None,
    }
