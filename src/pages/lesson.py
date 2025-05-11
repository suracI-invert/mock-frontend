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
from utils.visualize import paginate_df, filter_dataframe
from utils.network import get_httpx_client

from settings import get_settings

st.title("📜 Lessons")
sidebar()

st.markdown(
    """
    <style>
        /* Font size */
        .stDataFrame { font-size: 16px !important; }

        /* View size */
        .main .block-container { max-width: 90% !important; }

        /* nav */
        .nav-container {
            background-color: #004466;
            padding: 10px;
            border-radius: 10px;
            text-align: center;
        }
        .nav-container button {
            margin: 5px;
            padding: 10px 20px;
            font-size: 16px;
            border-radius: 8px;
            background-color: #0088cc;
            color: white;
            border: none;
            cursor: pointer;
            transition: 0.3s;
        }
        .nav-container button:hover {
            background-color: #006699;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


lesson_tab, create_lesson_tab = st.tabs(["Lessons", "Create lesson"])

with lesson_tab:
    lessons = get_lessons()
    for i, lesson in enumerate(lessons):
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            st.write(f"{lesson.id}. {lesson.name}")

        with col2:
            detail = st.popover("Show detail")

            lesson_str = parse_lesson_info(lesson)
            detail.write("---")
            for lstr in lesson_str:
                detail.write(lstr)
                detail.write("---")

        with col3:
            do_btn = st.button("Exercise", key=f"lesson_{lesson.id}_exercise_{i}")
            if do_btn:
                st.session_state.exercise_lesson = {"lesson_id": lesson.id}
                st.switch_page("pages/exercise.py")

with create_lesson_tab:
    create_lesson()
