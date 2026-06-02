from app.db.base import Base
from app.db.session import engine
from app.models import user, business, merchant_verification, menu_item, slot_capacity, menu_item_capacity, preorder, preorder_item, custom_request, proposal, subscription, review, saved_kitchen, admin_audit_log
from sqlalchemy import text


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    with engine.begin() as connection:
        connection.execute(
            text("CREATE UNIQUE INDEX IF NOT EXISTS uq_business_owner_user_id ON businesses (owner_user_id)")
        )
        connection.execute(
            text("ALTER TABLE subscriptions ADD COLUMN IF NOT EXISTS payment_type VARCHAR(20) NOT NULL DEFAULT 'free'")
        )


if __name__ == "__main__":
    init_db()
