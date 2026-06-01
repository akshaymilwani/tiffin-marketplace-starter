from datetime import date
from sqlalchemy.orm import Session

from app.models.subscription import Subscription


def activate_basic_plan(db: Session, business_id: str, admin_user_id: str) -> Subscription:
    subscription = Subscription(
        business_id=business_id,
        plan_tier="basic",
        status="active",
        activated_by=admin_user_id,
        start_date=date.today(),
    )
    db.add(subscription)
    db.commit()
    db.refresh(subscription)
    return subscription
