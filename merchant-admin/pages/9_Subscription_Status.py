import streamlit as st

from components.auth import require_merchant
from components.business_context import require_business
from components.api_client import api_get

st.title("Subscription Status")
require_merchant()
require_business()

try:
    data = api_get("/merchant/subscription")
except Exception as e:
    st.exception(e)
    st.stop()

subscription = data.get("subscription")
business = data["business"]

st.metric("Public listing", business["public_listing_status"])

if subscription:
    cols = st.columns(4)
    cols[0].metric("Plan", subscription["plan_tier"])
    cols[1].metric("Subscription type", subscription.get("payment_type", "free"))
    cols[2].metric("Status", subscription["status"])
    cols[3].metric("Renewal", subscription.get("renewal_date") or "Not set")

    st.subheader("Subscription details")
    st.write(f"Start date: {subscription.get('start_date') or 'Not set'}")
    st.write(f"End date: {subscription.get('end_date') or 'Not set'}")
    st.write(f"Notes: {subscription.get('notes') or 'None'}")
else:
    st.info("No active subscription. Ask an admin to activate a plan from Admin Console.")
