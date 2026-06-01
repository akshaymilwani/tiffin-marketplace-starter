import streamlit as st
from components.auth import require_login
from components.api_client import api_post

st.set_page_config(page_title="Business Profile", page_icon="🏪", layout="wide")

user_id = require_login()

st.title("🏪 Business Profile")

with st.form("business_form"):
    business_name = st.text_input("Business Name")
    cuisine_type = st.text_input("Cuisine Type")
    address_line1 = st.text_input("Address Line 1")
    city = st.text_input("City", value="Mississauga")
    province = st.text_input("Province", value="ON")
    postal_code = st.text_input("Postal Code")

    submitted = st.form_submit_button("Create Business")

if submitted:
    payload = {
        "business_name": business_name,
        "cuisine_type": cuisine_type,
        "address_line1": address_line1,
        "city": city,
        "province": province,
        "postal_code": postal_code,
    }

    try:
        result = api_post("/businesses", payload)
        st.session_state["business_id"] = result["id"]
        st.success("Business created successfully")
        st.json(result)
    except Exception as e:
        st.error("Error creating business")
        st.exception(e)
