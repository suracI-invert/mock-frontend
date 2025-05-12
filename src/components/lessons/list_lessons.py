from __future__ import annotations

from datetime import datetime
import streamlit as st
from ..callbacks import rerun_page
from models.lesson import (
    Lesson,
    ReadingLessonContent,
    ListeningLessonContent,
    SpeakingLessonContent,
    LessonContent,
    parse_level,
)

from utils.network import get_httpx_client, build_url, build_audio_url


def show_lesson_list():
    lessons = get_lessons()
    if lessons is None:
        st.error("Failed to get lessons")
        lessons = []
    col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
    with col1:
        st.header("Name")
        st.divider()
    with col2:
        st.header("Type")
        st.divider()
    with col3:
        st.header("Author")
        st.divider()
    with col4:
        st.header("Detail")
        st.divider()
    with col5:
        st.header("Action")
        st.divider()
    for i, lesson in enumerate(lessons):
        with st.container():
            col1, col2, col3, col4, col5 = st.columns(
                [2, 1, 1, 1, 1], vertical_alignment="center"
            )
            with col1:
                st.write(f"{lesson.id}. {lesson.name}")
            with col2:
                st.write(f"{lesson.type.value.upper()}")
            with col3:
                st.write(f"{lesson.author.name}")
            with col4:
                st.button(
                    "Detail",
                    key=f"lesson_detail_{lesson.id}",
                    on_click=show_detail,
                    args=(lesson,),
                )
            with col5:
                do_btn = st.button(
                    "Do",
                    key=f"lesson_do_{lesson.id}",
                )
                if do_btn:
                    st.session_state.exercise_lesson = {
                        "lesson_id": lesson.id,
                        "lesson": lesson,
                    }
                    st.switch_page("pages/exercise.py")


def get_lessons():
    with get_httpx_client() as client:
        resp = client.get(build_url("lesson/v1/list"))
        if resp.status_code == 200:
            return [Lesson.model_validate(lesson) for lesson in resp.json()]
        else:
            return None


@st.dialog("Detail")
def show_detail(lesson: Lesson):
    show_lesson_field("Lesson ID", str(lesson.id))
    show_lesson_field("Lesson Name", str(lesson.name))
    show_lesson_field("Lesson Type", lesson.type.value)
    show_lesson_field("Lesson Level", parse_level(lesson.level))
    show_lesson_field("Lesson Author", str(lesson.author.name))
    show_lesson_field("Lesson Created At", parse_datetime(lesson.createdAt))

    with st.expander("Lesson Content", expanded=False):
        show_lesson_content(lesson.content)


def parse_datetime(dt: datetime | None):
    if dt is None:
        return "N/A"
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def show_lesson_field(key: str, value: str):
    c1, c2 = st.columns([1, 3])
    with c1:
        st.write(f"{key}: ")
    with c2:
        st.write(value)


def show_lesson_content(content: LessonContent):
    if isinstance(content, ReadingLessonContent):
        st.write(content.text)
        st.divider()
        st.write("### Questions")
        for question in content.questions:
            with st.container(border=True):
                st.write("**Question:**")
                st.write(question.question)
                st.divider()
                for i, answer in enumerate(question.answers):
                    st.write(f"{i + 1}. {answer}")
    elif isinstance(content, ListeningLessonContent):
        st.write(content.transcript)
        st.audio(build_audio_url(content.audio_url))
        st.write("### Questions")
        for question in content.questions:
            with st.container(border=True):
                st.write("**Question:**")
                st.write(question.question)
                st.divider()
                for i, answer in enumerate(question.answers):
                    st.write(f"{i + 1}. {answer}")
    elif isinstance(content, SpeakingLessonContent):
        st.header(f"**{content.topic}**")
        st.divider()
        with st.container(border=True):
            st.write("**Topic Card**")
            st.divider()
            st.write(content.main_question)
            st.write("You can start by answering the following questions:")
            for guideline in content.guidelines:
                st.write(f"- {guideline}")
