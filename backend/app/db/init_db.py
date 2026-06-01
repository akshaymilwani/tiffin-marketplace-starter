from app.db.base import Base
from app.db.session import engine
from app.models import user, business, merchant_verification, menu_item, slot_capacity, menu_item_capacity, preorder, preorder_item, custom_request, proposal, subscription, review, saved_kitchen, admin_audit_log


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()
