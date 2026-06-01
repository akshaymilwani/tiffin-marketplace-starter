import streamlit as st

from components.auth import require_login
from components.business_context import require_business
from components.api_client import api_post

st.set_page_config(page_title="Menu Management", page_icon="🍱", layout="wide")

require_login()
business_id = require_business()

st.title("🍱 Menu Management")
st.caption(f"Business ID loaded automatically: {business_id}")

with st.form("menu_item_form"):
    name = st.text_input("Item Name", placeholder="Dal Tadka")
    description = st.text_area("Description", placeholder="Home-style dal with rice/roti option")
    price = st.number_input("Price", min_value=0.0, step=0.50, value=10.00)
    cuisine_tag = st.text_input("Cuisine Tag", value="Indian")
    dietary_tags_text = st.text_input("Dietary Tags comma-separated", value="vegetarian")
    spice_level = st.selectbox("Spice Level", ["mild", "medium", "spicy"])
    prep_lead_time_hours = st.number_input("Prep Lead Time Hours", min_value=0, step=1, value=4)

    available_days = st.multiselect(
        "Available Days",
        ["mon", "tue", "wed", "thu", "fri", "sat", "sun"],
        default=["mon", "tue", "wed", "thu", "fri"],
    )

    available_slots = st.multiselect(
        "Available Slots",
        ["lunch", "dinner"],
        default=["lunch", "dinner"],
    )

    submitted = st.form_submit_button("Add Menu Item")

if submitted:
    if not name:
        st.error("Item name is required.")
        st.stop()

    payload = {
        "business_id": business_id,
        "name": name,
        "description": description,
        "price": price,
        "cuisine_tag": cuisine_tag,
        "dietary_tags": [tag.strip() for tag in dietary_tags_text.split(",") if tag.strip()],
        "spice_level": spice_level,
        "prep_lead_time_hours": prep_lead_time_hours,
        "available_days": available_days,
        "available_slots": available_slots,
    }

    try:
        result = api_post("/menu-items", payload)
        st.success("Menu item added successfully.")
        st.json(result)
    except Exception as e:
        st.error("Failed to add menu item.")
        st.exception(e)
