from datetime import date, timedelta

import streamlit as st

from components.auth import require_admin
from components.api_client import api_get, api_post, api_put

st.title("Admin Console")
require_admin()

st.subheader("Create merchant login")
with st.form("create_merchant_login"):
    merchant_name = st.text_input("Merchant full name")
    merchant_email = st.text_input("Merchant email")
    merchant_password = st.text_input("Temporary password", type="password")
    create_merchant = st.form_submit_button("Create merchant user")

if create_merchant:
    try:
        result = api_post(
            "/auth/signup",
            {
                "full_name": merchant_name,
                "email": merchant_email,
                "password": merchant_password,
                "role": "merchant",
            },
            skip_auth=True,
        )
        st.success("Merchant login created.")
        st.code(f"email: {merchant_email}\npassword: {merchant_password}\nuser_id: {result['user_id']}")
    except Exception as e:
        st.exception(e)

st.subheader("Verification review")
status_filter = st.selectbox("Verification status", ["pending", "approved", "rejected", "all"])
path = "/admin/verifications" if status_filter == "all" else f"/admin/verifications?status={status_filter}"

try:
    verifications = api_get(path)
except Exception as e:
    st.exception(e)
    verifications = []

if verifications:
    st.dataframe(verifications, use_container_width=True, hide_index=True)
else:
    st.info("No verification submissions found.")

for verification in verifications:
    with st.expander(f"{verification['business_name']} - {verification['decision']}"):
        st.write(f"Certificate number: {verification.get('cert_number') or 'Not provided'}")
        st.write(f"Issuing authority: {verification.get('issuing_authority') or 'Not provided'}")
        st.write(f"Certificate file: {verification.get('cert_file_url') or 'Not provided'}")
        st.write(f"Address proof file: {verification.get('address_proof_file_url') or 'Not provided'}")
        st.write(f"Submitted at: {verification.get('submitted_at') or 'Not available'}")
        if verification.get("rejection_reason"):
            st.write(f"Rejection reason: {verification['rejection_reason']}")
        rejection_reason = st.text_area("Rejection reason", key=f"reject_reason_{verification['id']}")
        cols = st.columns(2)
        if cols[0].button("Approve", key=f"approve_{verification['id']}"):
            try:
                api_put(f"/admin/verifications/{verification['id']}/review", {"decision": "approved"})
                st.success("Verification approved and listing made visible.")
                st.rerun()
            except Exception as e:
                st.exception(e)
        if cols[1].button("Reject", key=f"reject_{verification['id']}"):
            try:
                api_put(
                    f"/admin/verifications/{verification['id']}/review",
                    {"decision": "rejected", "rejection_reason": rejection_reason},
                )
                st.success("Verification rejected.")
                st.rerun()
            except Exception as e:
                st.exception(e)

st.subheader("Subscriptions")
try:
    businesses = api_get("/admin/businesses")
except Exception as e:
    st.exception(e)
    businesses = []

if businesses:
    st.dataframe(businesses, use_container_width=True, hide_index=True)
    business_options = {f"{business['business_name']} ({business['id']})": business["id"] for business in businesses}

    st.subheader("Business approval")
    with st.form("business_review_form"):
        review_selected = st.selectbox("Business to review", list(business_options.keys()), key="business_review_selected")
        business_decision = st.selectbox("Decision", ["approved", "rejected", "pending"])
        business_rejection_reason = st.text_area("Rejection reason")
        review_business = st.form_submit_button("Save business decision")

    if review_business:
        try:
            result = api_put(
                f"/admin/businesses/{business_options[review_selected]}/review",
                {
                    "decision": business_decision,
                    "rejection_reason": business_rejection_reason,
                },
            )
            st.success("Business decision saved.")
            st.rerun()
        except Exception as e:
            st.exception(e)

    with st.form("subscription_form"):
        selected = st.selectbox("Business", list(business_options.keys()))
        plan_tier = st.selectbox("Plan", ["basic", "growth", "premium"])
        payment_type = st.selectbox("Subscription type", ["free", "paid"])
        renewal_date = st.date_input("Renewal date", value=date.today() + timedelta(days=30))
        notes = st.text_area("Admin notes")
        activate = st.form_submit_button("Activate subscription")

    if activate:
        try:
            result = api_post(
                f"/admin/businesses/{business_options[selected]}/subscription",
                {
                    "plan_tier": plan_tier,
                    "payment_type": payment_type,
                    "renewal_date": renewal_date.isoformat(),
                    "notes": notes,
                },
            )
            st.success("Subscription activated.")
            st.rerun()
        except Exception as e:
            st.exception(e)
else:
    st.info("No businesses found.")
