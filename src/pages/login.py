import streamlit as st
from utils.network import get_httpx_client
from components.user import get_user_info, UserInfo


st.set_page_config(
    page_title="My App Login",
    page_icon="🔑",
    layout="centered",
)


def login_screen():
    col1, col2, col3 = st.columns([1, 1, 1], vertical_alignment="center", gap="large")
    with col2:
        if st.button(
            "Log in with Google",
            type="primary",
            icon=":material/login:",
            use_container_width=True,
        ):
            st.login()


if not st.user.is_logged_in:
    login_screen()
else:
    st.switch_page("app.py")
