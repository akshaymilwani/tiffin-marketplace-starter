import streamlit as st
from components.api_client import api_get


def load_business_context(show_message: bool = False):
    """
    Loads the logged-in merchant's business into Streamlit session_state.

    Stores:
    - business_id
    - business_name
    - business_context
    """
    try:
        result = api_get("/merchant/my-business")
    except Exception as e:
        if show_message:
            st.warning(f"Could not load business context: {e}")
        return None

    if not result.get("business_found"):
        st.session_state.pop("business_id", None)
        st.session_state.pop("business_name", None)
        st.session_state.pop("business_context", None)

        if show_message:
            st.info("No business profile found yet. Please create one from Business Profile.")

        return None

    business = result["business"]

    st.session_state["business_id"] = business["id"]
    st.session_state["business_name"] = business["business_name"]
    st.session_state["business_context"] = business

    if show_message:
        st.sidebar.success(f"Business loaded: {business['business_name']}")

    return business


def require_business():
    """
    Use this on pages like Menu Management and Capacity Management.
    It guarantees business_id is present before continuing.
    """
    business_id = st.session_state.get("business_id")

    if business_id:
        return business_id

    business = load_business_context(show_message=True)

    if not business:
        st.error("Please create your business profile before using this page.")
        st.stop()

    return business["id"]
