import streamlit as st

from components.auth import login_box, logout_button

role = st.session_state.get("role")

if role == "admin":
    st.title("Tiffin Admin Console")
    st.write("Welcome to the admin console for business approvals, verification review, merchant accounts, and subscriptions.")
    st.write("Use the left sidebar to access admin dashboard and admin console.")
    logout_button()
elif role == "merchant":
    st.title("Welcome")
    st.write("Welcome to Tiffin Merchant app for managing your orders easily and keeping track of your business")
    st.write("Use the left sidebar to access dashboard, business profile, menu management, orders, and admin tools.")
    st.write('"People who love to eat are always the best people." - Julia Child')
    logout_button()
else:
    st.title("Welcome")
    st.write("Log in to access the Tiffin Merchant Portal or Admin Console.")
    login_box()
