from __future__ import annotations
from functools import partial
from typing import cast
import uuid
import streamlit as st

from models.lesson import (
    Lesson,
    LessonContent,
    LessonType,
    ListeningLessonContent,
    ReadingLessonContent,
    SpeakingLessonContent,
)
from utils.network import get_httpx_client, build_url
from ..chat import chat_sidebar


def do_exercise():
    lesson_id = st.session_state.get("exercise_lesson", {}).get("lesson_id", None)
    if not lesson_id:
        st.switch_page("pages/error.py")
    else:
        lesson = get_lesson(lesson_id)

        st.title(f"Exercise: {lesson.name}")

        display_exercise_session(lesson)


def get_lesson(lesson_id: int):
    lesson = st.session_state.exercise_lesson.get("lesson", None)
    if not lesson:
        with get_httpx_client() as client:
            resp = client.get(
                build_url(f"lesson/v1/{lesson_id}"),
            )
            if resp.status_code != 200:
                st.switch_page("pages/error.py")

            else:
                lesson = Lesson.model_validate(resp.json())
    else:
        lesson = Lesson.model_validate(lesson)
    return lesson


def get_lesson_content_main_text(lesson: Lesson):
    match lesson.type:
        case LessonType.READING:
            lesson.content = cast(ReadingLessonContent, lesson.content)
            return lesson.content.text
        case LessonType.SPEAKING:
            lesson.content = cast(SpeakingLessonContent, lesson.content)
            return lesson.content.main_question
        case LessonType.LISTENING:
            lesson.content = cast(ListeningLessonContent, lesson.content)
            return lesson.content.transcript


def turn_in(lesson: Lesson):
    text = get_lesson_content_main_text(lesson)
    st.session_state.exercise_lesson["final_data"] = {
        "lesson_id": lesson.id,
        "user_id": st.session_state.user_info.id,
        "text": text,
        "level": lesson.level,
        "lesson_type": lesson.type.value,
    }
    st.switch_page("pages/grade.py")


def parse_reading_content(content: ReadingLessonContent):
    s = f"Reading Exercise\n\n"
    s += f"Text: {content.text}\n\n"
    s += f"Questions:\n"
    for q in content.questions:
        s += f"Q: {q.question}\n"
        for i, a in enumerate(q.answers):
            s += f"{i + 1}. {a}\n"
    return s


def parse_listening_content(content: ListeningLessonContent):
    s = f"Listening Exercise\n\n"
    s += f"Transcript: {content.transcript}\n\n"
    s += f"Questions:\n"
    for q in content.questions:
        s += f"Q: {q.question}\n"
        for i, a in enumerate(q.answers):
            s += f"{i + 1}. {a}\n"
    return s


def parse_content(content: LessonContent):
    if isinstance(content, ReadingLessonContent):
        return parse_reading_content(content)
    elif isinstance(content, ListeningLessonContent):
        return parse_listening_content(content)
    else:
        return None


def get_initial_prompt(lesson: Lesson):
    prompt = """Please read the following exercise content and help me reason with the questions. 
Keep in mind that I am a language learner and I need your help to understand the content and answer the questions.
You should not give me the answers directly, but help me reason with the questions and give me hints (where to look at and how) to find the answers.
Here is the content:
{content}"""
    match lesson.type:
        case LessonType.READING:
            return prompt.format(content=parse_content(content=lesson.content))
        case LessonType.SPEAKING:
            return None
        case LessonType.LISTENING:
            return prompt.format(content=parse_content(content=lesson.content))
        case _:
            return None


def assistant(lesson: Lesson):
    if "assistant" not in st.session_state.exercise_lesson:
        st.session_state.exercise_lesson["assistant"] = {
            "session_id": uuid.uuid4().hex,
        }
    init_prompt = get_initial_prompt(lesson)
    if init_prompt:
        chat_sidebar(
            st.session_state.exercise_lesson["assistant"]["session_id"],
            initial_prompt=init_prompt,
        )
    else:
        st.error("Invalid lesson type for assistant")


def display_exercise_session(lesson: Lesson):
    st.button("Turn in", on_click=turn_in)
    st.button("Assistant", on_click=assistant, args=(lesson,))

    match lesson.type:
        case LessonType.READING:
            exercise_reading(lesson)
        case LessonType.LISTENING:
            exercise_listening(lesson)
        case LessonType.SPEAKING:
            # exercise_speaking(lesson)
            st.session_state.pop("exercise_lesson", None)
            st.switch_page("pages/error.py")
        case _:
            st.error("Invalid lesson type")


def format_answer_selectbox(i: int, answers: list[str]) -> str:
    return f"{i + 1}. {answers[i]}"


def exercise_reading(lesson: Lesson):

    content = cast(ReadingLessonContent, lesson.content)
    st.header("Reading Exercise: ", lesson.name)
    c1, c2 = st.columns(2)

    exercise_data = []

    with c1:
        st.header("Paragraph")
        st.write("---")
        st.write(content.text)
    with c2:
        st.header("Questions")
        st.write("---")
        for q in content.questions:
            st.write(q.question)
            no_ans = len(q.answers)
            for i, a in enumerate(q.answers):
                st.write(f"{i + 1}. {a}")

            format_answer_selectbox_p = partial(
                format_answer_selectbox, answers=q.answers
            )
            answer = st.selectbox(
                "Answer",
                options=[i for i in range(no_ans)],
                key=f"q_{q.index}_answer",
                format_func=format_answer_selectbox_p,
            )
            exercise_data.append(
                {
                    "index": q.index,
                    "question": q.question,
                    "answers": q.answers,
                    "student_answer": answer,
                }
            )
    st.session_state.exercise_lesson["data"] = exercise_data


def exercise_listening(lesson: Lesson):
    content = cast(ListeningLessonContent, lesson.content)
    st.header("Listening Exercise: ", lesson.name)

    exercise_data = []

    st.header("Audio")
    play_btn = st.button("Play", key="play_listening_audio")
    if play_btn:
        st.session_state.exercise_lesson["play_listening_audio"] = True
    if st.session_state.get("play_listening_audio", False):
        st.audio(content.audio_url, autoplay=True)
    st.write("---")
    st.header("Questions")
    st.write("---")
    for q in content.questions:
        st.write(q.question)
        no_ans = len(q.answers)
        for i, a in enumerate(q.answers):
            st.write(f"{i + 1}. {a}")

        format_answer_selectbox_p = partial(format_answer_selectbox, answers=q.answers)
        answer = st.selectbox(
            "Answer",
            options=[i for i in range(no_ans)],
            key=f"q_{q.index}_answer",
            format_func=format_answer_selectbox_p,
        )
        exercise_data.append(
            {
                "index": q.index,
                "question": q.question,
                "answers": q.answers,
                "student_answer": answer,
            }
        )
    st.session_state.exercise_lesson["data"] = exercise_data
