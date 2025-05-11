import streamlit as st
from components import sidebar
from settings import get_settings
from utils.network import get_httpx_client

st.title("🏠 Home Page")
st.write(f"Xin chào, {st.session_state.user_info.name}!")


sidebar()
