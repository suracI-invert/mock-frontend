import streamlit as st

from components.user import get_user_info, UserInfo

from utils.network import get_httpx_client

from settings import get_settings
import logfire

logfire.configure()


def login():
    user_info = get_user_info()
    if not user_info:
        with get_httpx_client() as client:
            resp = client.post(
                f"{get_settings().connection.backend_url.unicode_string()}user/v1/create",
                json={
                    "name": st.user.get("name"),
                    "email": st.user.get("email"),
                    "avatarUrl": st.user.get("picture", ""),
                    "is_logged_in": True,
                },
            )
            if resp.status_code == 404:
                raise RuntimeError("Failed to create user")

            user_info = UserInfo.model_validate(resp.json())

    if not user_info.is_logged_in:
        with get_httpx_client() as client:
            resp = client.post(
                f"{get_settings().connection.backend_url.unicode_string()}user/v1/update",
                json={
                    "id": user_info.id,
                    "name": user_info.name,
                    "email": user_info.email,
                    "avatarUrl": user_info.avatarUrl,
                    "is_logged_in": True,
                },
            )
            if resp.status_code == 404:
                raise RuntimeError("Failed to update user info")


if not st.user.is_logged_in:
    st.switch_page("pages/login.py")
else:
    login()
    st.switch_page("pages/home.py")
