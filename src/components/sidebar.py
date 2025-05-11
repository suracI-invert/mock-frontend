import streamlit as st
from .user import get_user_info


def make_sidebar():
    """Create a sidebar with navigation links."""
    if not st.user.is_logged_in:
        st.switch_page("app.py")
    else:
        with st.sidebar:
            # cool sidebar stuff

            st.title("Navigation 🧭")
            # st.page_link("pages/automate.py", label="Automate", icon="🤖")
            # st.page_link("pages/document_info.py", label="Document Info", icon="📄")
            st.page_link("pages/home.py", label="Home", icon="🏠")
            st.page_link("pages/account.py", label="Account", icon="📄")
            st.page_link("pages/lesson.py", label="Lesson", icon="📜")

            st.write("")
            st.write("")


sidebar = make_sidebar
