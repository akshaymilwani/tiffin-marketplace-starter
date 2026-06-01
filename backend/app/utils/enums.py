from enum import Enum

class UserRole(str, Enum):
    CUSTOMER = "customer"
    MERCHANT = "merchant"
    ADMIN = "admin"

class SlotType(str, Enum):
    LUNCH = "lunch"
    DINNER = "dinner"

class OrderStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    EXPIRED = "expired"
    PREPARING = "preparing"
    READY = "ready"
    FULFILLED = "fulfilled"
    CANCELLED = "cancelled"
