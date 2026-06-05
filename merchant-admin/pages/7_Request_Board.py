import streamlit as st

from components.auth import require_merchant
from components.business_context import require_business
from components.api_client import api_get, api_post

st.title("Request Board")
require_merchant()
require_business()

if st.session_state.pop("proposal_submitted_toast", False):
    st.toast("Proposal submitted.", icon="✅")

try:
    requests = api_get("/merchant/requests")
except Exception as e:
    st.exception(e)
    st.stop()

if not requests:
    st.info("No open customer requests.")
    st.stop()

st.dataframe(
    [
        {
            "title": request["title"],
            "cuisine": request["cuisine_tag"],
            "quantity": request["quantity"],
            "target_date": request["target_date"],
            "budget": f"${request['budget_min']:.2f} - ${request['budget_max']:.2f}",
            "location": request["location_text"],
        }
        for request in requests
    ],
    use_container_width=True,
    hide_index=True,
)

for request in requests:
    with st.expander(f"{request['title']} - {request['target_date']}"):
        st.write(request.get("description") or "")
        if request.get("dietary_notes"):
            st.write(f"Dietary notes: {request['dietary_notes']}")

        with st.form(f"proposal_{request['id']}"):
            quote_amount = st.number_input("Quote amount", min_value=0.01, step=1.0, value=max(float(request["budget_max"] or 1), 1.0))
            eta_notes = st.text_input("ETA / fulfillment notes")
            message = st.text_area("Message to customer")
            submitted = st.form_submit_button("Submit proposal")

        if submitted:
            try:
                api_post(
                    "/merchant/proposals",
                    {
                        "request_id": request["id"],
                        "quote_amount": quote_amount,
                        "eta_notes": eta_notes,
                        "message": message,
                    },
                )
                st.session_state["proposal_submitted_toast"] = True
                st.rerun()
            except Exception as e:
                st.exception(e)
