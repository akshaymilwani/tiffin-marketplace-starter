import streamlit as st

from components.auth import require_merchant
from components.api_client import api_get, api_post, api_put

require_merchant()

st.title("Business Profile")

try:
    current = api_get("/merchant/my-business")
except Exception as e:
    st.exception(e)
    current = {"business_found": False, "business": None}

business = current.get("business") if current.get("business_found") else None

if business:
    st.info("Your business profile is already set up. You can update the details below.")
else:
    st.info("Create your business profile to start managing menus, capacity, and orders.")

with st.form("business_form"):
    business_name = st.text_input("Business Name", value=business.get("business_name", "") if business else "")
    description = st.text_area("Description", value=business.get("description", "") if business else "")
    cuisine_type = st.text_input("Cuisine Type", value=business.get("cuisine_type", "") if business else "")
    address_line1 = st.text_input("Address Line 1", value=business.get("address_line1", "") if business else "")
    address_line2 = st.text_input("Address Line 2", value=business.get("address_line2", "") if business else "")
    city = st.text_input("City", value=business.get("city", "Mississauga") if business else "Mississauga")
    province = st.text_input("Province", value=business.get("province", "ON") if business else "ON")
    postal_code = st.text_input("Postal Code", value=business.get("postal_code", "") if business else "")
    pickup_enabled = st.checkbox("Pickup enabled", value=business.get("pickup_enabled", True) if business else True)
    self_delivery_enabled = st.checkbox(
        "Self delivery enabled",
        value=business.get("self_delivery_enabled", False) if business else False,
    )
    service_radius_km = st.number_input(
        "Service radius km",
        min_value=0.0,
        value=float(business.get("service_radius_km") or 0) if business else 0.0,
        step=1.0,
    )
    minimum_order_for_delivery = st.number_input(
        "Minimum order for delivery",
        min_value=0.0,
        value=float(business.get("minimum_order_for_delivery") or 0) if business else 0.0,
        step=1.0,
    )
    flat_delivery_fee = st.number_input(
        "Flat delivery fee",
        min_value=0.0,
        value=float(business.get("flat_delivery_fee") or 0) if business else 0.0,
        step=1.0,
    )
    service_zone_text = st.text_area("Service zone details", value=business.get("service_zone_text", "") if business else "")
    submitted = st.form_submit_button("Update Business" if business else "Create Business")

if submitted:
    payload = {
        "business_name": business_name,
        "description": description,
        "cuisine_type": cuisine_type,
        "pickup_enabled": pickup_enabled,
        "self_delivery_enabled": self_delivery_enabled,
        "service_radius_km": service_radius_km or None,
        "minimum_order_for_delivery": minimum_order_for_delivery or None,
        "flat_delivery_fee": flat_delivery_fee,
        "service_zone_text": service_zone_text,
        "address_line1": address_line1,
        "address_line2": address_line2,
        "city": city,
        "province": province,
        "postal_code": postal_code,
    }

    try:
        result = api_put("/merchant/my-business", payload) if business else api_post("/businesses", payload)
        st.session_state["business_id"] = result["id"]
        st.session_state["business_name"] = result["business_name"]
        st.session_state["business_context"] = result
        st.success("Business profile updated successfully" if business else "Business created successfully")
        st.rerun()
    except Exception as e:
        st.error("Error saving business profile")
        st.exception(e)
