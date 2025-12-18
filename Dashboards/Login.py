"""
Login UI and registration helper.
Provides a login form that authenticates users against the `users` table
in the `data/auth.db` SQLite database. Also includes a
"""

import streamlit as st
import bcrypt
from services.user_service import get_user_by_username, create_user


def login_form():
    st.subheader("Login Page")

    # --- LOGIN FORM ---
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

    if submitted:
        user = get_user_by_username(username)
        if user:
            # `user` is a User dataclass instance
            password_hash = user.password_hash
            if bcrypt.checkpw(password.encode(), password_hash.encode()):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.role = user.role
                st.success(f"Welcome, {username}!")
            else:
                st.error("Incorrect password")
        else:
            st.error("Username not found")

    # --- REGISTRATION ---
    with st.expander("New User? Register Here"):
        with st.form("register_form"):
            reg_username = st.text_input("New Username", key="reg_user")
            reg_password = st.text_input("New Password", type="password", key="reg_pass")
            role = st.selectbox("Role", ["Cybersecurity", "Data Science", "IT Operations", "Admin"])
            register = st.form_submit_button("Register")

        if register:
            if get_user_by_username(reg_username):
                st.error("Username already exists")
            else:
                hashed = bcrypt.hashpw(reg_password.encode(), bcrypt.gensalt())
                # create_user returns the created User
                create_user(reg_username, hashed.decode(), role)
                st.success("User registered! You can now log in.")
