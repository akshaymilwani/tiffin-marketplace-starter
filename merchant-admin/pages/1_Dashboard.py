import streamlit as st
from components.api_client import api_get

st.title("Dashboard")
col1, col2 = st.columns(2)
with col1:
    st.subheader("Merchant snapshot")
    st.json(api_get("/merchant/dashboard"))
with col2:
    st.subheader("Admin snapshot")
    st.json(api_get("/admin/dashboard"))
