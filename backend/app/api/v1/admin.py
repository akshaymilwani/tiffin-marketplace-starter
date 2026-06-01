from fastapi import APIRouter

router = APIRouter()

@router.get("/dashboard")
def admin_dashboard():
    return {
        "pending_verifications": 0,
        "active_merchants": 0,
        "expired_subscriptions": 0,
    }
