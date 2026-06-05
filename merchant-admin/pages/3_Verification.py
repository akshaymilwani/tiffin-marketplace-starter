import streamlit as st

from components.auth import require_merchant
from components.business_context import require_business
from components.api_client import api_get, api_post, api_put

st.title("Verification")
require_merchant()
require_business()

try:
    current = api_get("/merchant/verification")
except Exception as e:
    st.exception(e)
    st.stop()

business = current["business"]
verification = current.get("verification")

cols = st.columns(2)
cols[0].metric("Business status", business["verification_status"])
cols[1].metric("Public listing", business["public_listing_status"])

if verification:
    st.subheader("Latest submission")
    st.write(f"Decision: {verification.get('decision') or 'pending'}")
    st.write(f"Certificate number: {verification.get('cert_number') or 'Not provided'}")
    st.write(f"Issuing authority: {verification.get('issuing_authority') or 'Not provided'}")
    st.write(f"Certificate file: {verification.get('cert_file_url') or 'Not provided'}")
    st.write(f"Address proof file: {verification.get('address_proof_file_url') or 'Not provided'}")
    st.write(f"Submitted at: {verification.get('submitted_at') or 'Not available'}")
    if verification.get("rejection_reason"):
        st.write(f"Rejection reason: {verification['rejection_reason']}")

with st.form("verification_form"):
    cert_number = st.text_input(
        "Food handler / business certificate number",
        value=verification.get("cert_number", "") if verification else "",
    )
    issuing_authority = st.text_input(
        "Issuing authority",
        value=verification.get("issuing_authority", "") if verification else "",
    )
    cert_file_url = st.text_input(
        "Certificate file URL",
        value=verification.get("cert_file_url", "") if verification else "",
    )
    address_proof_file_url = st.text_input(
        "Address proof file URL",
        value=verification.get("address_proof_file_url", "") if verification else "",
    )
    submitted = st.form_submit_button("Update verification" if verification else "Submit verification")

if submitted:
    try:
        payload = {
            "cert_number": cert_number,
            "issuing_authority": issuing_authority,
            "cert_file_url": cert_file_url,
            "address_proof_file_url": address_proof_file_url,
        }
        if verification:
            api_put("/merchant/verification", payload)
        else:
            api_post("/merchant/verification", payload)
        st.success("Verification updated for admin review." if verification else "Verification submitted for admin review.")
        st.rerun()
    except Exception as e:
        st.exception(e)
