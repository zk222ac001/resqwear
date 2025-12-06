import streamlit as st

USERS = {
    "operator1": {"password": "op123", "role": "operator"},
    "dispatcher1": {"password": "dp123", "role": "dispatcher"},
}

def login():
    if "user" not in st.session_state:
        st.session_state.user = None

    if st.session_state.user:
        st.success(f"Logged in as {st.session_state.user['role'].upper()}")
        return st.session_state.user

    with st.sidebar.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        if submitted:
            user = USERS.get(username)
            if user and user["password"] == password:
                st.session_state.user = {"username": username, "role": user["role"]}
                st.success(f"Logged in as {user['role'].upper()}")
                st.rerun()
            else:
                st.error("Invalid username or password")
    return None

def require_role(role: str):
    user = st.session_state.get("user")
    if not user or user["role"] != role:
        st.warning(f"Access denied: requires '{role}' role")
        st.stop()
