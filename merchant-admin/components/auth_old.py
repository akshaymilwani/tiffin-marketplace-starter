import streamlit as st
from components.api_client import api_post

def login_box():
    st.sidebar.header("Login")

    email = st.sidebar.text_input("Email")
    password = st.sidebar.text_input("Password", type="password")

    if st.sidebar.button("Login"):
        if not email or not password:
            st.sidebar.error("Please enter email and password.")
            return

        try:
            result = api_post(
                "/auth/login",
                {
                    "email": email,
                    "password": password,
                },
                skip_auth=True,
            )

            st.session_state["user_id"] = result["user_id"]
            st.session_state["access_token"] = result.get("access_token")
            st.session_state["role"] = result.get("role", "merchant")

            st.sidebar.success("Logged in successfully")
            st.rerun()

        except Exception as e:
            st.sidebar.error(f"Login failed: {e}")

def logout_button():
    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.rerun()

def require_login():
    if "user_id" not in st.session_state:
        login_box()
        st.stop()

    logout_button()
    return st.session_state["user_id"]
