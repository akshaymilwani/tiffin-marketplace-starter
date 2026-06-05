import json
from urllib.parse import quote, unquote

import streamlit as st
import streamlit.components.v1 as components

from components.api_client import api_post
from components.business_context import load_business_context


SESSION_QUERY_KEYS = ("user_id", "access_token", "role")
SESSION_COOKIE_NAME = "tiffin_portal_session"
LOGOUT_QUERY_KEY = "_logout"
LOGGED_OUT_STATE_KEY = "logged_out"


def _query_value(key: str) -> str | None:
    value = st.query_params.get(key)
    if isinstance(value, list):
        return value[0] if value else None
    return value


def _persist_session(result: dict, default_role: str = "merchant"):
    role = result.get("role", default_role)
    access_token = result.get("access_token")

    st.session_state["user_id"] = result["user_id"]
    st.session_state["access_token"] = access_token
    st.session_state["role"] = role
    st.session_state[LOGGED_OUT_STATE_KEY] = False
    if LOGOUT_QUERY_KEY in st.query_params:
        del st.query_params[LOGOUT_QUERY_KEY]


def _session_payload_from_cookie() -> dict | None:
    raw_cookie = st.context.cookies.get(SESSION_COOKIE_NAME)
    if not raw_cookie:
        return None

    try:
        payload = json.loads(unquote(raw_cookie))
    except (TypeError, ValueError):
        return None

    if not isinstance(payload, dict):
        return None
    return payload


def _apply_session_payload(payload: dict | None):
    if not payload:
        return

    user_id = payload.get("user_id")
    access_token = payload.get("access_token")
    role = payload.get("role")

    if not user_id or not access_token or role not in {"merchant", "admin"}:
        return

    st.session_state["user_id"] = user_id
    st.session_state["access_token"] = access_token
    st.session_state["role"] = role


def _write_session_cookie():
    user_id = st.session_state.get("user_id")
    access_token = st.session_state.get("access_token")
    role = st.session_state.get("role")

    if not user_id or not access_token or role not in {"merchant", "admin"}:
        return

    payload = quote(json.dumps({"user_id": user_id, "access_token": access_token, "role": role}))
    components.html(
        f"""
        <script>
        document.cookie = "{SESSION_COOKIE_NAME}={payload}; path=/; max-age=604800; SameSite=Lax";
        </script>
        """,
        height=0,
    )


def sync_persisted_session():
    if _query_value(LOGOUT_QUERY_KEY) == "1":
        st.session_state.clear()
        st.session_state[LOGGED_OUT_STATE_KEY] = True
        _clear_persisted_session()
        _expire_session_cookie()
        return

    if st.session_state.get(LOGGED_OUT_STATE_KEY):
        _clear_persisted_session()
        _expire_session_cookie()
        return

    if st.session_state.get("user_id") and st.session_state.get("access_token"):
        _write_session_cookie()
        return

    user_id = _query_value("user_id")
    access_token = _query_value("access_token")
    role = _query_value("role")

    if user_id and access_token and role in {"merchant", "admin"}:
        _apply_session_payload({"user_id": user_id, "access_token": access_token, "role": role})
        _write_session_cookie()
        return

    _apply_session_payload(_session_payload_from_cookie())
    _write_session_cookie()


def _clear_persisted_session():
    for key in SESSION_QUERY_KEYS:
        if key in st.query_params:
            del st.query_params[key]


def _expire_session_cookie():
    cookie_expiry = f"{SESSION_COOKIE_NAME}=; path=/; max-age=0; expires=Thu, 01 Jan 1970 00:00:00 GMT; SameSite=Lax"
    components.html(
        f"""
        <script>
        const expiredCookie = "{cookie_expiry}";
        document.cookie = expiredCookie;
        try {{
          window.parent.document.cookie = expiredCookie;
        }} catch (error) {{}}
        </script>
        """,
        height=0,
    )


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
                _persist_session(result, role)
                if result.get("role", role) == "merchant":
                    load_business_context(show_message=False)
                st.sidebar.success(f"{role.title()} login created.")
                st.rerun()
            except Exception as e:
                st.sidebar.error(f"Signup failed: {e}")


def login_box():
    sync_persisted_session()
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

            _persist_session(result)

            if result.get("role") == "merchant":
                load_business_context(show_message=True)

            st.sidebar.success("Logged in successfully")
            st.rerun()

        except Exception as e:
            st.sidebar.error(f"Login failed: {e}")

    st.sidebar.divider()
    _signup_form("merchant", "Create merchant login")


def logout_button():
    st.sidebar.markdown(
        """
        <a href="/?_logout=1" target="_self" style="
            display:block;
            width:100%;
            text-align:center;
            padding:0.45rem 0.75rem;
            border:1px solid rgba(49, 51, 63, 0.2);
            border-radius:0.5rem;
            color:inherit;
            text-decoration:none;
        ">Logout</a>
        """,
        unsafe_allow_html=True,
    )


def require_login():
    sync_persisted_session()

    if "user_id" not in st.session_state:
        login_box()
        st.stop()

    if st.session_state.get("role") == "merchant" and "business_id" not in st.session_state:
        load_business_context(show_message=False)

    logout_button()
    return st.session_state["user_id"]


def require_merchant():
    require_login()

    if st.session_state.get("role") != "merchant":
        st.error("This page is only available to merchant users.")
        st.stop()

    return st.session_state["user_id"]


def require_admin():
    require_login()

    if st.session_state.get("role") != "admin":
        st.error("Admin Console is only available to admin users.")
        st.stop()

    return st.session_state["user_id"]
