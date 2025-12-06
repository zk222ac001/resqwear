import streamlit as st
import hashlib
import time

# -----------------------------
#  SECURE USER DATABASE
# -----------------------------
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

USERS = {
    "operator1": {"password": hash_password("op123"), "role": "operator"},
    "dispatcher1": {"password": hash_password("dp123"), "role": "dispatcher"},
}

# -----------------------------
#  Initialize session state
# -----------------------------
def init_session():
    defaults = {
        "user": None,
        "failed_attempts": 0,
        "lockout_until": 0,
        "login_timestamp": None,
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)

# -----------------------------
# Login function
# -----------------------------
def login(session_timeout_min: int = 30):
    init_session()

    # SESSION TIMEOUT CHECK
    if st.session_state.user:
        elapsed = time.time() - st.session_state.login_timestamp
        if elapsed > session_timeout_min * 60:
            st.warning("Session expired. Please log in again.")
            st.session_state.user = None
            st.session_state.login_timestamp = None
            st.rerun()

    # Already logged in?
    if st.session_state.user:
        st.sidebar.success(
            f"Logged in as {st.session_state.user['username']} ({st.session_state.user['role']})"
        )
        if st.sidebar.button("Logout"):
            st.session_state.user = None
            st.session_state.login_timestamp = None
            st.rerun()
        return st.session_state.user

    # LOCKOUT CHECK
    if time.time() < st.session_state.lockout_until:
        wait = int(st.session_state.lockout_until - time.time())
        st.sidebar.error(f"Too many failed attempts. Try again in {wait}s.")
        return None

    # LOGIN FORM
    with st.sidebar.form("login_form"):
        st.header("🔐 Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

        if submitted:
            user = USERS.get(username)

            if user and user["password"] == hash_password(password):
                st.session_state.user = {"username": username, "role": user["role"]}
                st.session_state.login_timestamp = time.time()
                st.session_state.failed_attempts = 0
                st.success(f"Logged in successfully as {user['role'].upper()}")
                st.rerun()
            else:
                st.session_state.failed_attempts += 1
                st.error("Invalid username or password")

                # LOCKOUT AFTER 3 FAILED ATTEMPTS
                if st.session_state.failed_attempts >= 3:
                    st.session_state.lockout_until = time.time() + 30
                    st.error("Too many failed attempts. Locked for 30 seconds.")
                    st.session_state.failed_attempts = 0
    return None

# -----------------------------
# Role-based Protection
# -----------------------------
def require_role(role: str):
    user = st.session_state.get("user")

    if not user:
        st.error("You must log in to access this page.")
        st.stop()

    if user["role"] != role:
        st.error(f"Access denied: '{role}' role required")
        st.stop()
