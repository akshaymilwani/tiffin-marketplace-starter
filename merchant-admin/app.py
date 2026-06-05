import streamlit as st

from navigation import run_navigation

st.set_page_config(page_title="Tiffin Portal", layout="wide")
run_navigation()
st.write('"People who love to eat are always the best people." - Julia Child')
