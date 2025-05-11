import streamlit as st
from pydantic import BaseModel

from settings import get_settings

from utils.network import get_httpx_client


class UserInfo(BaseModel):
    id: int
    name: str
    email: str
    avatarUrl: str
    is_logged_in: bool


def get_user_info(force: bool = True):
    email = st.user.get("email")
    assert isinstance(email, str)
    if force:
        with get_httpx_client() as client:
            resp = client.get(
                f"{get_settings().connection.backend_url.unicode_string()}user/v1/"
                + email
            )
            if resp.status_code == 200:
                st.session_state.user_info = UserInfo.model_validate(resp.json())
                return st.session_state.user_info

    user_info = st.session_state.get("user_info", None)
    if user_info:
        return UserInfo.model_validate(user_info)

    if not user_info:
        with get_httpx_client() as client:
            resp = client.get(
                f"{get_settings().connection.backend_url.unicode_string()}user/v1/"
                + email
            )
            if resp.status_code == 200:
                st.session_state.user_info = UserInfo.model_validate(resp.json())
                return st.session_state.user_info


def display_user_info():
    user_info = get_user_info()
    if user_info:
        st.image(user_info.avatarUrl)
        c1, c2 = st.columns([1, 3])
        with c1:
            st.write("Name")
        with c2:
            st.write(user_info.name)
        with c1:
            st.write("Email")
        with c2:
            st.write(user_info.email)
        is_edit_info = st.session_state.get("edit_user_info", False)
        prev_edit_status = st.session_state.get("edit_user_info_status", None)
        if prev_edit_status == "successful":
            st.success("User info updated")
            st.session_state.edit_user_info_status = None
        elif prev_edit_status == "failed":
            st.error("Failed to update user info")
            st.session_state.edit_user_info_status = None
        if not is_edit_info:
            edit = st.button("Edit")
            if edit:
                st.session_state.edit_user_info = True
                st.switch_page("pages/account.py")
        else:
            c1, c2 = st.columns([1, 3])
            with c1:
                st.write("New name")
            with c2:
                new_name = st.text_input(
                    "New Name",
                    key="new_name",
                    value=user_info.name,
                    placeholder=user_info.name,
                )
            with c1:
                st.write("New email")
            with c2:
                new_email = st.text_input(
                    "New Email",
                    key="new_email",
                    value=user_info.email,
                    placeholder=user_info.email,
                )
            update = st.button("Update")
            if update:
                with get_httpx_client() as client:
                    resp = client.post(
                        f"{get_settings().connection.backend_url.unicode_string()}user/v1/update",
                        json={
                            "id": user_info.id,
                            "name": new_name,
                            "email": new_email,
                            "avatarUrl": user_info.avatarUrl,
                            "is_logged_in": True,
                        },
                    )
                    if resp.status_code == 200:
                        st.session_state.edit_user_info = False
                        get_user_info(force=True)
                        st.session_state.edit_user_info_status = "successful"
                    else:
                        print(resp.text)
                        st.session_state.edit_user_info = False
                        st.session_state.edit_user_info_status = "failed"
                st.switch_page("pages/account.py")
    else:
        st.error("Failed to get user info")
