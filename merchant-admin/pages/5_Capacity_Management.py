import streamlit as st

from components.auth import require_merchant
from components.business_context import require_business
from components.api_client import api_get, api_post

st.title("Capacity Management")
require_merchant()
require_business()

st.caption("Unconfigured lunch/dinner slots default to capacity 20. Saving capacity here overwrites that default for the selected date and slot.")

with st.form("capacity_form"):
    service_date = st.date_input("Service date")
    slot_type = st.selectbox("Slot", ["lunch", "dinner"])
    total_capacity = st.number_input("Total capacity", min_value=1, step=1, value=20)
    is_closed = st.checkbox("Close this slot")
    submitted = st.form_submit_button("Save capacity")

if submitted:
    try:
        api_post(
            "/merchant/capacity",
            {
                "service_date": service_date.isoformat(),
                "slot_type": slot_type,
                "total_capacity": total_capacity,
                "is_closed": is_closed,
            },
        )
        st.success("Capacity saved.")
        st.rerun()
    except Exception as e:
        st.error("Failed to save capacity.")
        st.exception(e)

try:
    slots = api_get("/merchant/capacity")
    st.subheader("Configured slots")
    if slots:
        st.dataframe(slots, use_container_width=True, hide_index=True)
    else:
        st.info("No capacity configured yet.")
except Exception as e:
    st.exception(e)
