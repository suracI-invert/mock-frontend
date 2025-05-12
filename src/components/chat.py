from typing import cast
from .user import get_user_info
import streamlit as st

from utils.network import get_httpx_client
from .infra.backend.client import build_url


def get_avatar_url():
    user_info = get_user_info()
    if user_info:
        return user_info.avatarUrl
    return None


def display_chat_history(session_id: str, header: str, history: list[dict[str, str]]):
    for i, h in enumerate(history):
        if h.get("role") == "user":
            with st.chat_message("User", avatar=get_avatar_url()):
                st.write(f"{h['content']}")
        elif h.get("role") == "assistant":
            with st.chat_message("assistant"):
                st.write(f"{h['content']}")


def get_assistant_response(session_id: str, message: str):
    user_info = get_user_info()
    with get_httpx_client() as client:
        url = build_url("chat/v1/stream")
        with client.stream(
            "POST",
            url,
            json={
                "message": message,
                "conversation_id": session_id,
                "lang": st.session_state.chat_session["lang"],
                "user": user_info.name if user_info else "Anonymous",
            },
        ) as stream_resp:
            if stream_resp.status_code == 200:
                for token in stream_resp.iter_text():
                    yield token


def handle_user_input(session_id: str, message: str):
    st.session_state.chat_session["history"].append(
        {"role": "user", "content": message}
    )
    with st.chat_message("user", avatar=get_avatar_url()):
        st.write(f"{message}")
    response_stream = get_assistant_response(session_id, message)
    if not response_stream:
        st.error("Failed to get response")
        response_stream = ["Failed to get response"]
    with st.chat_message("assistant"):
        response_text = st.write_stream(response_stream)

    st.session_state.chat_session["history"].append(
        {"role": "assistant", "content": response_text}
    )


def display_chat(session_id: str):
    if "chat_session" not in st.session_state:
        st.session_state.chat_session = {
            "session_id": session_id,
            "history": [],
            "start": True,
        }
    elif session_id != st.session_state.chat_session["session_id"]:
        st.session_state.chat_session = {
            "session_id": session_id,
            "history": [],
            "start": True,
        }

    if st.session_state.chat_session["start"]:
        st.session_state.chat_session["start"] = False
        lang = st.selectbox("Select language", ["English", "Vietnamese"])
        st.session_state.chat_session["lang"] = lang.lower()
    else:
        history = cast(list[dict[str, str]], st.session_state.chat_session["history"])

        display_chat_history(session_id, "Chat History", history)
        message = st.chat_input("Input here")
        if message:
            handle_user_input(session_id, message)
