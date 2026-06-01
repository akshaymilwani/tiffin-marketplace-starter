from fastapi import APIRouter

router = APIRouter()

@router.get("/dashboard")
def merchant_dashboard():
    return {
        "pending_orders": 0,
        "verification_status": "pending",
        "subscription_status": "inactive",
        "open_requests": 0,
    }
