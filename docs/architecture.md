# Architecture

- Customer UI: Next.js
- Merchant/Admin UI: Streamlit
- Backend API: FastAPI
- Database: PostgreSQL

Keep business rules in the backend service layer, especially:
- capacity enforcement
- listing visibility rules
- request acceptance / proposal auto-close logic
- manual subscription gating
