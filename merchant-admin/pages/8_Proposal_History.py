import streamlit as st

from components.auth import require_login
from components.business_context import require_business
from components.api_client import api_get

st.title("Proposal History")
require_login()
require_business()

try:
    proposals = api_get("/merchant/proposals")
except Exception as e:
    st.exception(e)
    st.stop()

if not proposals:
    st.info("No proposals submitted yet.")
else:
    st.dataframe(proposals, use_container_width=True, hide_index=True)
