from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import db_dep, get_mock_user_id
from app.models.custom_request import CustomRequest
from app.models.proposal import Proposal
from app.schemas.custom_request import CustomRequestCreate
from app.services.request_service import create_request

router = APIRouter()


class ProposalStatusUpdate(BaseModel):
    status: str


def _money(value):
    return float(value or 0)


def _iso(value):
    return value.isoformat() if value else None


def _serialize_request(request: CustomRequest) -> dict:
    return {
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


def _serialize_proposal(proposal: Proposal) -> dict:
    return {
        "id": str(proposal.id),
        "request_id": str(proposal.request_id),
        "business_id": str(proposal.business_id),
        "quote_amount": _money(proposal.quote_amount),
        "eta_notes": proposal.eta_notes,
        "message": proposal.message,
        "status": proposal.status,
        "created_at": _iso(proposal.created_at),
    }


@router.post("")
def create_request_route(payload: CustomRequestCreate, db: Session = Depends(db_dep), user_id: str = Depends(get_mock_user_id)):
    return create_request(db, user_id, payload)


@router.get("")
def list_my_requests(db: Session = Depends(db_dep), user_id: str = Depends(get_mock_user_id)):
    requests = (
        db.query(CustomRequest)
        .filter(CustomRequest.user_id == user_id)
        .order_by(CustomRequest.created_at.desc())
        .all()
    )
    return [_serialize_request(request) for request in requests]


@router.get("/{request_id}")
def get_my_request(request_id: UUID, db: Session = Depends(db_dep), user_id: str = Depends(get_mock_user_id)):
    request = db.query(CustomRequest).filter(CustomRequest.id == request_id, CustomRequest.user_id == user_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")

    proposals = db.query(Proposal).filter(Proposal.request_id == request.id).order_by(Proposal.created_at.desc()).all()
    return {
        "request": _serialize_request(request),
        "proposals": [_serialize_proposal(proposal) for proposal in proposals],
    }


@router.put("/{request_id}/proposals/{proposal_id}/status")
def update_proposal_status(
    request_id: UUID,
    proposal_id: UUID,
    payload: ProposalStatusUpdate,
    db: Session = Depends(db_dep),
    user_id: str = Depends(get_mock_user_id),
):
    if payload.status not in {"accepted", "rejected"}:
        raise HTTPException(status_code=400, detail="Proposal status must be accepted or rejected")

    request = db.query(CustomRequest).filter(CustomRequest.id == request_id, CustomRequest.user_id == user_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")

    proposal = db.query(Proposal).filter(Proposal.id == proposal_id, Proposal.request_id == request.id).first()
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")

    proposal.status = payload.status
    proposal.updated_at = datetime.utcnow()

    if payload.status == "accepted":
        request.status = "accepted"
        db.query(Proposal).filter(
            Proposal.request_id == request.id,
            Proposal.id != proposal.id,
            Proposal.status != "rejected",
        ).update({"status": "rejected", "updated_at": datetime.utcnow()}, synchronize_session=False)
    elif not db.query(Proposal).filter(Proposal.request_id == request.id, Proposal.status != "rejected").first():
        request.status = "open"

    request.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(proposal)
    db.refresh(request)

    return {"request": _serialize_request(request), "proposal": _serialize_proposal(proposal)}
