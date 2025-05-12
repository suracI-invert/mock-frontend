from __future__ import annotations

from typing import cast
import uuid
from .user import get_user_info
import streamlit as st
from utils.network import get_httpx_client
from utils.network import build_url


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


def kickoff_initial_prompt(session_id: str, initial_prompt: str):
    response_stream = get_assistant_response(session_id, initial_prompt)
    if not response_stream:
        st.error("Failed to get response")
        response_stream = ["Failed to get response"]
    with st.chat_message("assistant"):
        response_text = st.write_stream(response_stream)
    st.session_state.chat_session["kickoff_finished"] = True
    st.session_state.chat_session["history"].append(
        {"role": "assistant", "content": response_text}
    )
    st.rerun(scope="fragment")


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


def display_chat(session_id: str, initial_prompt: str | None = None):
    if "chat_session" not in st.session_state:
        st.session_state.chat_session = {
            "session_id": session_id,
            "history": [],
            "start": True,
            "kickoff_finished": False,
        }
    elif session_id != st.session_state.chat_session["session_id"]:
        st.session_state.chat_session = {
            "session_id": session_id,
            "history": [],
            "start": True,
            "kickoff_finished": False,
        }

    if st.session_state.chat_session["start"]:
        st.session_state.chat_session["start"] = False
        with st.form(key="chat_lang_form", clear_on_submit=True):
            lang = st.selectbox("Select language", ["Vietnamese", "English"])
            st.session_state.chat_session["lang"] = lang.lower()
            submit = st.form_submit_button("Submit")
            if submit:
                st.session_state.chat_session["lang"] = lang.lower()
                st.session_state.chat_session["start"] = False
    else:
        message = st.chat_input("Input here")
        with st.container(height=750):
            if initial_prompt and not st.session_state.chat_session.get(
                "kickoff_finished"
            ):
                kickoff_initial_prompt(session_id, initial_prompt)
            history = cast(
                list[dict[str, str]], st.session_state.chat_session["history"]
            )
            display_chat_history(session_id, "Chat History", history)
            if message:
                handle_user_input(session_id, message)


@st.fragment
def fragment_chat_sidebar(session_id: str, initial_prompt: str | None = None):
    st.title("Chat Assistant")
    reset_btn = st.button("Start New Chat")
    if reset_btn:
        st.session_state.chat_session["session_id"] = uuid.uuid4().hex
        st.rerun(scope="fragment")
    display_chat(session_id, initial_prompt)


def chat_sidebar(session_id: str, initial_prompt: str | None = None):
    print(session_id)
    with st.sidebar:
        fragment_chat_sidebar(session_id, initial_prompt)
    return session_id
