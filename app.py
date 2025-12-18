# to run this app, use the command: python -m streamlit run app.py
"""
Main Streamlit launcher for the Multi-Domain Intelligence Platform.
"""
from dotenv import load_dotenv
load_dotenv()

import streamlit as st

# Set page config
st.set_page_config(page_title="Multi-Domain Intelligence Platform", layout="wide")

# Session state for login
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "role" not in st.session_state:
    st.session_state.role = ""

# Sidebar title
st.sidebar.title("Navigation")

# --- LOGIN LOGIC ---
if not st.session_state.logged_in:
    st.header(" Login")
    from Dashboards.Login import login_form
    login_form()
else:
    role = st.session_state.role.lower()
    st.sidebar.write(f"Logged in as: {st.session_state.username} ({st.session_state.role})")

    # --- Determine available pages ---
    Dashboards = {}
    from Dashboards.Cybersecurity import dashboard as cyber_dash
    from Dashboards.Data_Science import dashboard as ds_dash
    from Dashboards.IT_Operations import dashboard as it_dash

    if role == "admin":
        # Admin sees all dashboards
        Dashboards["Cybersecurity"] = cyber_dash
        Dashboards["Data Science"] = ds_dash
        Dashboards["IT Operations"] = it_dash
        st.sidebar.info(" Admin Mode: Access to all dashboards")
    elif role == "cybersecurity":
        Dashboards["Cybersecurity"] = cyber_dash
    elif role == "data science":
        Dashboards["Data Science"] = ds_dash
    elif role == "it operations":
        Dashboards["IT Operations"] = it_dash

    # --- Sidebar selectbox ---
    if Dashboards:
        dashboard_names = list(Dashboards.keys())
        selected = st.sidebar.selectbox("Go to Dashboard", dashboard_names, index=0)
        Dashboards[selected]()  # call the selected dashboard
    else:
        st.sidebar.info("No dashboards available for your role. Please contact an admin or log out.")
        st.write("No dashboards available for your role.")
