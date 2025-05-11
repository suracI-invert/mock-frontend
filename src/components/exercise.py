import uuid
from pydantic import BaseModel
import streamlit as st

from .user import get_user_info
from .lesson import Lesson
from .lesson import Question
from .sidebar import make_sidebar
from utils.network import get_httpx_client
from settings import get_settings


class QuestionNoKey(BaseModel):
    index: int
    question: str
    answers: list[str]


class ReadingExerciseContent(BaseModel):
    text: str
    questions: list[QuestionNoKey]


class ListeningExerciseContent(BaseModel):
    audio_url: str
    transcript: str
    questions: list[QuestionNoKey]


class SpeakingExerciseContent(BaseModel):
    topic: str
    main_question: str
    guidelines: list[str]


class ExerciseWithKey(BaseModel):
    index: int
    question: str
    answers: list[str]
    student_answer: int
    correct_answer: int


class Grade(BaseModel):
    exercises: list[ExerciseWithKey]
    score: int
    max_score: int
    overall_comment: str
    detail_comment: str
    suggestions: str


def exercise_reading(lesson: Lesson):
    content = ReadingExerciseContent.model_validate(lesson.content)
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
            _, ca = st.columns([1, 4])
            no_ans = len(q.answers)
            with ca:
                for i, a in enumerate(q.answers):
                    st.write(f"{i + 1}. {a}")

            answer = st.selectbox(
                "Answer",
                options=[i for i in range(1, no_ans + 1)],
                key=f"q_{q.index}_answer",
            )
            answer -= 1
            exercise_data.append(
                {
                    "index": q.index,
                    "question": q.question,
                    "answers": q.answers,
                    "student_answer": answer,
                }
            )
    st.session_state.exercise_lesson["data"] = exercise_data
    return content.text, exercise_data


def exercise_listening(lesson: Lesson):
    content = ListeningExerciseContent.model_validate(lesson.content)
    st.header("Listening Exercise: ", lesson.name)
    c1, c2 = st.columns(2)

    exercise_data = []

    with c1:
        st.header("Audio")
        st.write("---")
        st.audio(content.audio_url, autoplay=True)
    with c2:
        st.header("Questions")
        st.write("---")
        for q in content.questions:
            st.write(q.question)
            _, ca = st.columns([1, 4])
            no_ans = len(q.answers)
            with ca:
                for i, a in enumerate(q.answers):
                    st.write(f"{i + 1}. {a}")

            answer = st.selectbox(
                "Answer",
                options=[i for i in range(1, no_ans + 1)],
                key=f"q_{q.index}_answer",
            )
            answer -= 1
            exercise_data.append(
                {
                    "index": q.index,
                    "question": q.question,
                    "answers": q.answers,
                    "student_answer": answer,
                }
            )
    st.session_state.exercise_lesson["data"] = exercise_data
    return content.transcript, exercise_data


def display_speaking():
    user_info = get_user_info()
    _data = st.session_state.speaking_session.get("data", {})
    assert isinstance(_data, dict)
    if "history" in _data:
        _history: dict[str, list[dict[str, str]]] = _data.get(["history"], {})

        for p, h in _history.items():
            st.write(f"Part {p}")
            st.write("---")
            for i, q in enumerate(h):
                if q.get("role") == "user":
                    with st.chat_message(
                        user_info.name if user_info else "User",
                        avatar=user_info.avatarUrl if user_info else None,
                    ):
                        st.write(f"{q['content']}")
                elif q.get("role") == "assistant":
                    with st.chat_message("assistant"):
                        st.write(f"{q['content']}")
    q_btn = st.button("Quit")
    if q_btn:
        st.switch_page("pages/lesson.py")


def exercise_speaking(lesson: Lesson):
    user_info = get_user_info()
    if "speaking_session" not in st.session_state:
        st.session_state.speaking_session = {
            "session_id": uuid.uuid4().hex,
            "part": "p1",
            "end": False,
        }
    if st.session_state.speaking_session["end"]:
        display_speaking()

    else:
        session_id = st.session_state.speaking_session["session_id"]
        part = st.session_state.speaking_session["part"]
        audio_input = st.audio_input("Audio Input")
        if audio_input:
            with st.chat_message(
                user_info.name if user_info else "User",
                avatar=user_info.avatarUrl if user_info else None,
            ):
                st.audio(audio_input)
                with get_httpx_client() as client:
                    resp = client.post(
                        f"{get_settings().connection.backend_url.unicode_string()}resources/v1/audio/text",
                        content=audio_input.getvalue(),
                    )
                    if resp.status_code == 200:
                        transcript = resp.json()["transcript"]
                        st.write(transcript)
                        chat_resp = client.post(
                            f"{get_settings().connection.backend_url.unicode_string()}exercise/v1/speaking",
                            json={
                                "session_id": session_id,
                                "part": part,
                                "content": transcript,
                                "topic": lesson.content.get("topic", ""),
                                "main_question": lesson.content.get(
                                    "main_question", ""
                                ),
                                "guidelines": lesson.content.get("guidelines", []),
                                "level": lesson.level.value,
                            },
                        )
                        if chat_resp.status_code == 200:
                            st.session_state.speaking_session["data"] = chat_resp.json()
                    else:
                        st.error("Failed to transcript ")

        _data = st.session_state.speaking_session.get("data", {})
        assert isinstance(_data, dict)
        current_resp = _data.get("response", "")
        with get_httpx_client() as client:
            resp = client.post(
                f"{get_settings().connection.backend_url.unicode_string()}resources/v1/audio/convert",
                json={"transcript": current_resp},
            )
            if resp.status_code == 200:
                with st.chat_message("assistant"):
                    st.audio(resp.content)
                    st.write(current_resp)
        if "history" in _data:
            _history: dict[str, list[dict[str, str]]] = _data.get("history", {})

            for p, h in _history.items():
                st.write(f"Part {p}")
                st.write("---")
                for i, q in enumerate(h):
                    if q.get("role") == "user":
                        with st.chat_message(
                            user_info.name if user_info else "User",
                            avatar=user_info.avatarUrl if user_info else None,
                        ):
                            st.write(f"{q['content']}")
                    elif q.get("role") == "assistant":
                        with st.chat_message("assistant"):
                            st.write(f"{q['content']}")
        if _data.get("is_end", False):
            st.session_state.speaking_session["end"] = True


def grade(
    lesson_id: int,
    user_id: int,
    transcript: str,
    level: int,
    lesson_type: str,
):
    d = {
        "lesson_id": lesson_id,
        "user_id": user_id,
        "transcript": transcript if transcript else "",
        "level": level,
        "lesson_type": lesson_type,
        "questions": st.session_state.exercise_lesson["data"],
    }
    with get_httpx_client() as client:
        resp = client.post(
            f"{get_settings().connection.backend_url.unicode_string()}exercise/v1/grade",
            json=d,
        )
        if resp.status_code != 200:
            st.error("Failed to submit exercise")
            print(resp.text)
        else:
            data = Grade.model_validate(resp.json())
            c1, c2 = st.columns([1, 4])
            with c1:
                st.write("Score:")
            with c2:
                st.write(f"{data.score}/{data.max_score}")
            st.write("---")
            st.write(data.overall_comment)
            st.write("---")
            st.write(data.detail_comment)
            st.write("---")
            st.write(data.suggestions)
