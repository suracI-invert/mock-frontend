import uuid
import streamlit as st
from components import sidebar
from settings import get_settings
from utils.network import get_httpx_client
from components.chat import display_chat

st.set_page_config(page_title=None, page_icon=None, layout="wide", menu_items=None)


st.title("🏠 Home Page")
st.write(f"Xin chào, {st.session_state.user_info.name}!")

if "home" not in st.session_state:
    st.session_state.home = {}

chat_btn = st.button("Chat with me")
if chat_btn:
    st.session_state.home["chat_session_id"] = uuid.uuid4().hex

if "chat_session_id" in st.session_state.home:
    refresh_btn = st.button("Refresh Chat")
    if refresh_btn:
        st.session_state.home["chat_session_id"] = uuid.uuid4().hex
        st.rerun()
    close_chat_btn = st.button("Close Chat")
    if close_chat_btn:
        st.session_state.home.pop("chat_session_id", None)
        st.rerun()
    c1, c2 = st.columns([2, 1])
    with c2:
        display_chat(st.session_state.home["chat_session_id"])

sidebar()
