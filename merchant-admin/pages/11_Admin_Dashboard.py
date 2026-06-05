import pandas as pd
import streamlit as st

from components.auth import require_admin
from components.api_client import api_get

st.title("Admin Dashboard")
require_admin()

try:
    dashboard = api_get("/admin/dashboard")
except Exception as e:
    st.exception(e)
    st.stop()

top_metric_cols = st.columns(3)
top_metric_cols[0].metric("Total merchants", dashboard.get("total_merchants", 0))
top_metric_cols[1].metric("Active merchants", dashboard.get("active_merchants", 0))
top_metric_cols[2].metric("Pending verification", dashboard.get("pending_verifications", 0))

bottom_metric_cols = st.columns(2)
bottom_metric_cols[0].metric("Merchants added within last 30 days", dashboard.get("merchants_added_last_30_days", 0))
bottom_metric_cols[1].metric("Total orders placed", dashboard.get("total_orders", 0))

st.subheader("Top 3 active merchants")
top_active = dashboard.get("top_active_merchants", [])
if top_active:
    st.dataframe(pd.DataFrame(top_active), use_container_width=True, hide_index=True)
else:
    st.info("No merchant activity yet.")

st.subheader("Bottom 3 merchants by activity")
least_active = dashboard.get("least_active_merchants", [])
if least_active:
    st.dataframe(pd.DataFrame(least_active), use_container_width=True, hide_index=True)
else:
    st.info("No merchants found.")
