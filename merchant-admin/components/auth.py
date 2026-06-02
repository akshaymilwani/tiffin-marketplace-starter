import streamlit as st

from components.api_client import api_post
from components.business_context import load_business_context


def _signup_form(role: str, label: str):
    with st.sidebar.expander(label):
        full_name = st.text_input("Full name", key=f"{role}_signup_name")
        email = st.text_input("Email", key=f"{role}_signup_email")
        password = st.text_input("Password", type="password", key=f"{role}_signup_password")

        if st.button(f"Create {role} login", key=f"{role}_signup_button"):
            if not full_name or not email or not password:
                st.sidebar.error("Name, email, and password are required.")
                return

            try:
                result = api_post(
                    "/auth/signup",
                    {
                        "full_name": full_name,
                        "email": email,
                        "password": password,
                        "role": role,
                    },
                    skip_auth=True,
                )
                st.session_state["user_id"] = result["user_id"]
                st.session_state["access_token"] = result.get("access_token")
                st.session_state["role"] = result.get("role", role)
                load_business_context(show_message=False)
                st.sidebar.success(f"{role.title()} login created.")
                st.rerun()
            except Exception as e:
                st.sidebar.error(f"Signup failed: {e}")


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

            load_business_context(show_message=True)

            st.sidebar.success("Logged in successfully")
            st.rerun()

        except Exception as e:
            st.sidebar.error(f"Login failed: {e}")

    st.sidebar.divider()
    _signup_form("merchant", "Create merchant login")
    _signup_form("admin", "Create first admin login")


def logout_button():
    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.rerun()


def require_login():
    if "user_id" not in st.session_state:
        login_box()
        st.stop()

    if "business_id" not in st.session_state:
        load_business_context(show_message=False)

    logout_button()
    return st.session_state["user_id"]


def require_admin():
    require_login()

    if st.session_state.get("role") != "admin":
        st.error("Admin Console is only available to admin users.")
        st.stop()

    return st.session_state["user_id"]
