# Tiffin Marketplace Starter

Monorepo starter for a preorder-first marketplace for tiffin services, cloud kitchens, and local food businesses.

## Stack
- Customer app: Next.js
- Merchant/Admin app: Streamlit
- Backend API: FastAPI + SQLAlchemy + PostgreSQL
- Local dev: Docker Compose

## Apps
- `backend/` FastAPI API and business logic
- `customer-web/` Next.js customer-facing web app
- `merchant-admin/` Streamlit merchant/admin portal

## Quick start
1. Copy `.env.example` files if needed.
2. Start local services:
   ```bash
   docker compose up --build
   ```
3. Open:
   - Customer web: http://localhost:3000
   - Merchant/Admin: http://localhost:8501
   - Backend API docs: http://localhost:8000/docs

## Suggested build order
1. Finish auth
2. Finish business onboarding + verification
3. Finish menu + capacity CRUD
4. Finish preorder flow
5. Finish request board + proposals
6. Finish admin moderation + manual subscription activation

## Notes
- This starter focuses on the MVP flow: verified merchants, preorder slots, request board, and manual subscription activation.
- Payments are modeled as off-platform in v1.
