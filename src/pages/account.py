import streamlit as st

from components import sidebar
from components.user import get_user_info, display_user_info
from utils.network import get_httpx_client
from settings import get_settings

st.title("📜 Account Page")

display_user_info()

if st.button("Log out"):
    user_info = get_user_info()
    if user_info:
        with get_httpx_client() as client:
            resp = client.post(
                f"{get_settings().connection.backend_url.unicode_string()}user/v1/update",
                json={
                    "name": user_info.name,
                    "email": user_info.email,
                    "avatarUrl": user_info.avatarUrl,
                    "is_logged_in": False,
                },
            )
            if resp.status_code == 404:
                raise RuntimeError("Failed to update user info")
    st.logout()

sidebar()
