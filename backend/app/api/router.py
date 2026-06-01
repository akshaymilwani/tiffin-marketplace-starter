from fastapi import APIRouter
from app.api.v1 import auth, businesses, menu_items, orders, requests, merchant, admin

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(businesses.router, prefix="/businesses", tags=["businesses"])
api_router.include_router(menu_items.router, prefix="/menu-items", tags=["menu-items"])
api_router.include_router(orders.router, prefix="/orders", tags=["orders"])
api_router.include_router(requests.router, prefix="/requests", tags=["requests"])
api_router.include_router(merchant.router, prefix="/merchant", tags=["merchant"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
