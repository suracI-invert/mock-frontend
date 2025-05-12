import uuid
import streamlit as st
from streamlit_elements import elements, mui, html
from components import sidebar
from settings import get_settings
from utils.network import get_httpx_client
from components.chat import chat_sidebar
from components.user import get_user_info, UserInfo

st.set_page_config(page_title=None, page_icon=None, layout="wide", menu_items=None)

user_info = get_user_info()

name = user_info.name if user_info else "Guest"
st.title("🏠 Home Page")
st.write(f"Xin chào, {name}!")

if "home" not in st.session_state:
    st.session_state.home = {}

chat_btn = st.button("Chat with me")
if chat_btn:
    st.session_state.home["chat_session_id"] = uuid.uuid4().hex

# if "chat_session_id" in st.session_state.home:
#     chat_sidebar(st.session_state.home["chat_session_id"], "Hello, I need help?")

sidebar()
