import streamlit as st
import pandas as pd

from components import sidebar
from components.lesson import (
    get_lessons,
    parse_lesson_info,
    create_reading_lesson,
    display_lesson,
    create_lesson,
)

from components.lessons.list_lessons import show_detail


from utils.visualize import paginate_df, filter_dataframe
from utils.network import get_httpx_client

from settings import get_settings

st.set_page_config(
    page_title="Lessons",
    page_icon="📜",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("📜 Lessons")
sidebar()


lesson_tab, create_lesson_tab = st.tabs(["Lessons", "Create lesson"])

with lesson_tab:
    from components.lessons.list_lessons import show_lesson_list

    show_lesson_list()

with create_lesson_tab:
    create_lesson()
