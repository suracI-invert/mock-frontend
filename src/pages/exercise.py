import streamlit as st
from utils.network import get_httpx_client
from components.lesson import Lesson
from components.lesson import LessonType
from components.exercise import (
    exercise_reading,
    exercise_speaking,
    grade,
    exercise_listening,
)
from settings import get_settings

if "exercise_lesson" not in st.session_state:
    print("Switching pgae guard")
    st.switch_page("/pages/lesson.py")
else:
    lesson_id = st.session_state.get("exercise_lesson", {}).get("lesson_id", None)
    if not lesson_id:
        st.error("Invalid lesson")
        st.session_state.pop("exercise_lesson", None)
        back_btn = st.button("Back")
        if back_btn:
            st.switch_page("pages/lesson.py")

    else:
        lesson = st.session_state.exercise_lesson.get("lesson", None)
        if not lesson:
            with get_httpx_client() as client:
                resp = client.get(
                    f"{get_settings().connection.backend_url.unicode_string()}lesson/v1/{lesson_id}"
                )
                if resp.status_code != 200:
                    st.error("Failed to retrieve lesson")
                    st.session_state.pop("exercise_lesson", None)
                    back_btn = st.button("Back")
                    if back_btn:
                        st.switch_page("pages/lesson.py")

                else:
                    lesson = Lesson.model_validate(resp.json())
        else:
            lesson = Lesson.model_validate(lesson)

        st.title(f"Exercise: {lesson.name}")

        turn_in_btn = st.button("Turn in")
        if turn_in_btn:
            text = lesson.content.get("transcript", None)
            if not text:
                text = lesson.content.get("text", "")

            st.session_state.exercise_lesson["final_data"] = {
                "lesson_id": lesson_id,
                "user_id": st.session_state.user_info.id,
                "transcript": text,
                "level": lesson.level,
                "lesson_type": lesson.type.value,
            }
            st.switch_page("pages/grade.py")
        else:
            match lesson.type:
                case LessonType.READING:
                    transcript, exercise_data = exercise_reading(lesson)
                case LessonType.LISTENING:
                    transcript, exercise_data = exercise_listening(lesson)
                case LessonType.SPEAKING:
                    # exercise_speaking(lesson)
                    st.session_state.pop("exercise_lesson", None)
                    st.switch_page("pages/error.py")
