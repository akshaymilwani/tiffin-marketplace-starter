import streamlit as st

from components.auth import sync_persisted_session


def run_navigation():
    sync_persisted_session()
    logged_out = st.session_state.get("logged_out")
    role = st.session_state.get("role")

    welcome_page = st.Page("pages/0_Welcome.py", title="Welcome")
    merchant_pages = [
        welcome_page,
        st.Page("pages/1_Dashboard.py", title="Dashboard"),
        st.Page("pages/2_Business_Profile.py", title="Business Profile"),
        st.Page("pages/3_Verification.py", title="Verification"),
        st.Page("pages/4_Menu_Management.py", title="Menu Management"),
        st.Page("pages/5_Capacity_Management.py", title="Capacity Management"),
        st.Page("pages/6_Orders_Inbox.py", title="Orders Inbox"),
        st.Page("pages/7_Request_Board.py", title="Request Board"),
        st.Page("pages/8_Proposal_History.py", title="Proposal History"),
        st.Page("pages/9_Subscription_Status.py", title="Subscription Status"),
    ]
    admin_pages = [
        welcome_page,
        st.Page("pages/11_Admin_Dashboard.py", title="Admin Dashboard"),
        st.Page("pages/10_Admin_Console.py", title="Admin Console"),
    ]
    if logged_out:
        pages = {"Portal": [welcome_page]}
    elif role == "admin":
        pages = {"Admin": admin_pages}
    elif role == "merchant":
        pages = {"Merchant": merchant_pages}
    else:
        pages = {"Portal": [welcome_page]}

    st.navigation(pages).run()
