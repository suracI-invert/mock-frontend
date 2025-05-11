from typing import Any, Literal
from pydantic import BaseModel
from enum import Enum
import streamlit as st

from utils.network import get_httpx_client
from settings import get_settings


class LessonType(str, Enum):
    READING = "reading"
    LISTENING = "listening"
    SPEAKING = "speaking"


class Level(int, Enum):
    A1 = 1
    A2 = 2
    B1 = 3
    B2 = 4
    C1 = 5
    C2 = 6


def parse_level(level: Level):
    if level == Level.A1:
        return "A1"
    elif level == Level.A2:
        return "A2"
    elif level == Level.B1:
        return "B1"
    elif level == Level.B2:
        return "B2"
    elif level == Level.C1:
        return "C1"
    elif level == Level.C2:
        return "C2"


def parse_level_inv(level: str):
    if level == "A1":
        return Level.A1
    elif level == "A2":
        return Level.A2
    elif level == "B1":
        return Level.B1
    elif level == "B2":
        return Level.B2
    elif level == "C1":
        return Level.C1
    elif level == "C2":
        return Level.C2
    else:
        raise ValueError()


class Lesson(BaseModel):
    id: int
    name: str
    description: str
    type: LessonType
    level: Level
    author: dict[str, str | int]
    content: dict[str, Any]


def get_lessons():
    with get_httpx_client() as client:
        lessons: list[Lesson] = []
        resp = client.get(
            f"{get_settings().connection.backend_url.unicode_string()}lesson/v1/list"
        )
        if resp.status_code == 200:
            return [Lesson.model_validate(lesson) for lesson in resp.json()]
        else:
            return lessons


def parse_lesson_info(lesson: Lesson):
    lesson_detail: list[str] = []
    lesson_detail.append(f"**Name**: {lesson.name}\n")
    lesson_detail.append(f"**Description**: {lesson.description}\n")
    lesson_detail.append(f"**Type**: {lesson.type.value.upper()}\n")
    lesson_detail.append(f"**Level**: {parse_level((lesson.level))}\n")
    lesson_detail.append(f"**Author**: {lesson.author.get("name", "")}\n")
    return lesson_detail


def create_lesson():
    lesson_name = st.text_input("Lesson name", key="lesson_name")
    lesson_description = st.text_area("Description", key="lesson_description")
    lesson_type = st.selectbox(
        "Type",
        ["Reading", "Listening", "Speaking"],
        key="lesson_type",
    )
    lesson_level = st.selectbox(
        "Level",
        ["A1", "A2", "B1", "B2", "C1", "C2"],
        key="lesson_level",
    )
    if lesson_type == "Reading":
        create_reading_lesson(
            lesson_name, lesson_description, lesson_type.lower(), lesson_level
        )
    elif lesson_type == "Listening":
        create_listening_lesson(
            lesson_name, lesson_description, lesson_type.lower(), lesson_level
        )
    elif lesson_type == "Speaking":
        create_speaking_lesson(
            lesson_name, lesson_description, lesson_type.lower(), lesson_level
        )
    else:
        st.error("Not impplemented")


class Question(BaseModel):
    index: int
    text: str
    answers: list[str]
    correct_answer: int


class GeneratedReadingLesson(BaseModel):
    text: str
    questions: list[Question]


class GeneratedListeningLesson(BaseModel):
    transcript: str
    questions: list[Question]


class GeneratedSpeakingLesson(BaseModel):
    topic: str
    main_question: str
    guidelines: list[str]


def generate_reading_lesson_call(text: str, level: int):
    with get_httpx_client() as client:
        resp = client.post(
            f"{get_settings().connection.backend_url.unicode_string()}lesson/v1/generate",
            json={
                "text": text,
                "level": level,
                "type": "reading",
            },
        )
        if resp.status_code != 200:
            return None
        else:
            content = GeneratedReadingLesson.model_validate(resp.json()["content"])
            return content


def generate_listening_lesson_call(transcript: str, level: int):
    with get_httpx_client() as client:
        resp = client.post(
            f"{get_settings().connection.backend_url.unicode_string()}lesson/v1/generate",
            json={
                "transcript": transcript,
                "level": level,
                "type": "listening",
            },
        )
        if resp.status_code != 200:
            return None
        else:
            content = GeneratedListeningLesson.model_validate(resp.json()["content"])
            return content


def generate_audio(transcript: str):
    with get_httpx_client() as client:
        audio_resp = client.post(
            f"{get_settings().connection.backend_url.unicode_string()}resources/v1/audio/convert",
            json={
                "transcript": transcript,
            },
        )
        if audio_resp.status_code != 200:
            return None
        audioUrl = f"{get_settings().connection.backend_url.unicode_string()}resources/v1/audio/{audio_resp.json()["uid"]}"
        return audioUrl


def generate_reading_lesson(text: str, level: int):
    content = generate_reading_lesson_call(text, level)
    if not content:
        st.error("Failed to generate reading lesson")
    else:
        qs = []
        for question in content.questions:
            qs.append(
                Question(
                    index=question.index,
                    text=question.text,
                    answers=question.answers,
                    correct_answer=question.correct_answer,
                ).model_dump()
            )
        st.session_state.creating_lesson_data["questions"] = qs


def generate_listening_lesson(transcript: str, level: int):
    content = generate_listening_lesson_call(transcript, level)
    if not content:
        st.error("Failed to generate listening lesson")
    else:
        qs = []
        for question in content.questions:
            qs.append(
                Question(
                    index=question.index,
                    text=question.text,
                    answers=question.answers,
                    correct_answer=question.correct_answer,
                ).model_dump()
            )
        st.session_state.creating_lesson_data["questions"] = qs


def fill_questions(text: str, level: str, num_q: int, num_a):
    st.write("Please fill in the questions")
    questions = []
    for i in range(num_q):
        _question_value = (
            st.session_state.creating_lesson_data["questions"][i].get("text", "")
            if i < len(st.session_state.creating_lesson_data["questions"])
            else ""
        )
        question_text = st.text_input(
            f"Question {i + 1}", value=_question_value, placeholder=_question_value
        )
        if question_text == "":
            st.session_state.creating_lesson_valid = "Question must not be empty"

        answers = []
        c1, c2 = st.columns([1, 4])
        for j in range(num_a):
            with c2:
                _answer_value = (
                    st.session_state.creating_lesson_data["questions"][i].get(
                        "answers", ["" for _ in range(num_a)]
                    )[j]
                    if i < len(st.session_state.creating_lesson_data["questions"])
                    else ""
                )
                answer_text = st.text_input(
                    f"Answer {j + 1}",
                    value=_answer_value,
                    placeholder=_answer_value,
                    key=f"question_{i}_answer_{j}",
                )
                if answer_text == "":
                    st.session_state.creating_lesson_valid = "Answer must not be empty"
                answers.append(answer_text)
        _correct_answer_value = (
            st.session_state.creating_lesson_data["questions"][i].get(
                "correct_answer", 0
            )
            if i < len(st.session_state.creating_lesson_data["questions"])
            else 0
        )
        correct_answer = st.selectbox(
            f"Correct answer for question {i + 1}",
            [j for j in range(num_a)],
            index=_correct_answer_value,
        )
        questions.append(
            {
                "index": i,
                "text": question_text,
                "answers": answers,
                "correct_answer": correct_answer,
            }
        )
    return questions


def creating_reading_lesson_p1(level: str):
    st.write("Please enter the paragraph")
    text = st.text_area("Paragraph (Maximun 2000 words)", key="text", height=34 * 10)
    if len(text.split(" ")) > 2000:
        st.session_state.creating_lesson_valid = (
            "Paragraph must be less than 2000 words"
        )
    elif len(text.split(" ")) < 10:
        st.session_state.creating_lesson_valid = "Paragraph must be more than 10 words"
    generate = st.button("Generate")
    if generate:
        if text == "":
            st.error("Paragraph must not be empty")
        else:
            generate_reading_lesson(text, parse_level_inv(level))
    _questions = st.session_state.creating_lesson_data.get("questions", None)
    _num_questions = len(_questions) if _questions else 4
    _num_answer_each = (
        len(_questions[0].get("answers", []))
        if _questions and len(_questions) > 0
        else 2
    )
    if _num_answer_each == 0:
        _num_answer_each = 2
    num_questions = st.selectbox(
        "Number of questions",
        [i for i in range(4, 11)],
        index=[i for i in range(4, 11)].index(_num_questions),
    )
    num_answer_each = st.selectbox(
        "Number of answers",
        [i for i in range(2, 5)],
        index=[i for i in range(2, 5)].index(_num_answer_each),
    )
    return text, num_questions, num_answer_each


def creating_listening_lesson_p1(level: str):
    st.write("Please enter the transcript")
    text = st.text_area("Transcript (Maximun 2000 words)", key="text", height=34 * 10)
    if len(text.split(" ")) > 2000:
        st.session_state.creating_lesson_valid = (
            "Transcript must be less than 2000 words"
        )
    elif len(text.split(" ")) < 10:
        st.session_state.creating_lesson_valid = "Transcript must be more than 10 words"
    c1, c2 = st.columns(2)
    with c1:
        generate_audio_btn = st.button("Generate Audio")
        if generate_audio_btn:
            if text == "":
                st.error("Transcript must not be empty")
            else:
                audio_url = generate_audio(text)
                if not audio_url:
                    st.error("Failed to generate audio")
                else:
                    st.session_state.creating_lesson_data["audio_url"] = audio_url
    with c2:
        generate = st.button("Generate")
        if generate:
            if text == "":
                st.error("Transcript must not be empty")
            else:
                generate_reading_lesson(text, parse_level_inv(level))
    if st.session_state.creating_lesson_data.get("audio_url", None):
        st.audio(st.session_state.creating_lesson_data["audio_url"])

    _questions = st.session_state.creating_lesson_data.get("questions", None)
    _num_questions = len(_questions) if _questions else 4
    _num_answer_each = (
        len(_questions[0].get("answers", []))
        if _questions and len(_questions) > 0
        else 2
    )
    if _num_answer_each == 0:
        _num_answer_each = 2
    num_questions = st.selectbox(
        "Number of questions",
        [i for i in range(4, 11)],
        index=[i for i in range(4, 11)].index(_num_questions),
    )
    num_answer_each = st.selectbox(
        "Number of answers",
        [i for i in range(2, 5)],
        index=[i for i in range(2, 5)].index(_num_answer_each),
    )
    return text, num_questions, num_answer_each


def display_lesson():
    if "creating_lesson_data" not in st.session_state:
        st.switch_page("pages/lesson.py")
    else:
        c1, c2 = st.columns([1, 3])
        with c1:
            st.write("Name:")
        with c2:
            st.write(st.session_state.creating_lesson_info.get("name", ""))
        c1, c2 = st.columns([1, 3])
        with c1:
            st.write("Description:")
        with c2:
            st.write(st.session_state.creating_lesson_info.get("description", ""))
        c1, c2 = st.columns([1, 3])
        with c1:
            st.write("Type:")
        with c2:
            st.write(st.session_state.creating_lesson_info.get("type", ""))
        c1, c2 = st.columns([1, 3])
        with c1:
            st.write("Level:")
        with c2:
            st.write(st.session_state.creating_lesson_info.get("level", ""))
        finish = st.button("Finish")
        if finish:
            st.session_state.pop("creating_lesson_data", None)
            st.session_state.pop("creating_lesson_valid", None)
            st.session_state.pop("creating_lesson_finished", None)
            st.session_state.pop("creating_lesson_info", None)
            st.switch_page("pages/lesson.py")


def create_reading_lesson(name: str, description: str, lesson_type: str, level: str):
    if "creating_lesson_data" not in st.session_state:
        st.session_state.creating_lesson_valid = "ok"
        st.session_state.creating_lesson_data = {"questions": [], "current": "reading"}
        st.session_state.creating_lesson_data_finished = False
        st.session_state.creating_lesson_info = {}
    elif st.session_state.creating_lesson_data.get("current", None) != "reading":
        st.session_state.creating_lesson_valid = "ok"
        st.session_state.creating_lesson_data_finished = False
        st.session_state.creating_lesson_data = {
            "current": "reading",
            "questions": [],
        }
        st.session_state.creating_lesson_info = {}

    st.session_state.creating_lesson_valid = "ok"
    c1, c2 = st.columns(2)
    with c1:
        text, num_questions, num_answer_each = creating_reading_lesson_p1(level)
    with c2:
        st.session_state.creating_lesson_data["questions"] = fill_questions(
            text,
            level,
            num_questions,
            num_answer_each,
        )

    submitted = st.button("Submit")
    if submitted:
        if st.session_state.creating_lesson_valid == "ok":
            with get_httpx_client() as client:
                resp = client.post(
                    f"{get_settings().connection.backend_url.unicode_string()}lesson/v1/upload",
                    json={
                        "data": {
                            "authorId": st.session_state.user_info.id,
                            "name": name,
                            "description": description,
                            "type": lesson_type,
                            "level": parse_level_inv(level),
                            "content": {
                                "text": text,
                                "questions": st.session_state.creating_lesson_data[
                                    "questions"
                                ],
                            },
                        },
                    },
                )
                if resp.status_code == 200:

                    st.session_state.creating_lesson_data_finished = True
                    st.session_state.creating_lesson_info = {
                        "name": name,
                        "description": description,
                        "type": lesson_type,
                        "level": level,
                    }
                    st.success("Uploaded successfully")
                    st.switch_page("pages/display.py")

                else:
                    st.error("Failed to upload")
                    print(resp.text)

        else:
            st.error(st.session_state.creating_lesson_valid)


def create_listening_lesson(name: str, description: str, lesson_type: str, level: str):
    if "creating_lesson_data" not in st.session_state:
        st.session_state.creating_lesson_valid = "ok"
        st.session_state.creating_lesson_data = {
            "current": "listening",
            "questions": [],
        }
        st.session_state.creating_lesson_data_finished = False
        st.session_state.creating_lesson_info = {}
    elif st.session_state.creating_lesson_data.get("current", None) != "listening":
        st.session_state.creating_lesson_valid = "ok"
        st.session_state.creating_lesson_data_finished = False
        st.session_state.creating_lesson_data = {
            "current": "listening",
            "questions": [],
        }
        st.session_state.creating_lesson_info = {}

    st.session_state.creating_lesson_valid = "ok"
    c1, c2 = st.columns(2)
    with c1:
        text, num_questions, num_answer_each = creating_listening_lesson_p1(level)
    with c2:
        st.session_state.creating_lesson_data["questions"] = fill_questions(
            text,
            level,
            num_questions,
            num_answer_each,
        )

    submitted = st.button("Submit")
    if submitted:
        if st.session_state.creating_lesson_valid == "ok":
            with get_httpx_client() as client:
                resp = client.post(
                    f"{get_settings().connection.backend_url.unicode_string()}lesson/v1/upload",
                    json={
                        "data": {
                            "authorId": st.session_state.user_info.id,
                            "name": name,
                            "description": description,
                            "type": lesson_type,
                            "level": parse_level_inv(level),
                            "content": {
                                "transcript": text,
                                "audio_url": st.session_state.creating_lesson_data[
                                    "audio_url"
                                ],
                                "questions": st.session_state.creating_lesson_data[
                                    "questions"
                                ],
                            },
                        },
                    },
                )
                if resp.status_code == 200:

                    st.session_state.creating_lesson_data_finished = True
                    st.session_state.creating_lesson_info = {
                        "name": name,
                        "description": description,
                        "type": lesson_type,
                        "level": level,
                    }
                    st.success("Uploaded successfully")
                    st.switch_page("pages/display.py")
                else:
                    st.error("Failed to upload")
                    print(resp.text)

        else:
            st.error(st.session_state.creating_lesson_valid)


def generate_speaking_lesson_call(topic: str, level: int):
    with get_httpx_client() as client:
        resp = client.post(
            f"{get_settings().connection.backend_url.unicode_string()}lesson/v1/generate",
            json={
                "text": topic,
                "level": level,
                "type": "speaking",
            },
        )
        if resp.status_code != 200:
            return None
        else:
            content = GeneratedSpeakingLesson.model_validate(resp.json()["content"])
            return content


def generate_speaking_lesson(topic: str, level: str):
    content = generate_speaking_lesson_call(topic, parse_level_inv(level))
    if not content:
        st.error("Failed to generate speaking lesson")
    else:
        st.session_state.creating_lesson_data["questions"] = content.model_dump()


def create_speaking_lesson(name: str, description: str, lesson_type: str, level: str):
    if "creating_lesson_data" not in st.session_state:
        st.session_state.creating_lesson_valid = "ok"
        st.session_state.creating_lesson_data = {
            "current": "speaking",
            "questions": {},
        }
        st.session_state.creating_lesson_data_finished = False
        st.session_state.creating_lesson_info = {}
    elif st.session_state.creating_lesson_data.get("current", None) != "speaking":
        st.session_state.creating_lesson_valid = "ok"
        st.session_state.creating_lesson_data_finished = False
        st.session_state.creating_lesson_data = {
            "current": "speaking",
            "questions": {},
        }
        st.session_state.creating_lesson_info = {}

    st.session_state.creating_lesson_valid = "ok"

    topic = st.text_input("Topic", key="speaking_topic")
    if topic == "":
        st.session_state.creating_lesson_valid = "Topic cannot be empty"
    generate_button = st.button("Generate", key="speaking_generate")
    if generate_button:
        if topic == "":
            st.session_state.creating_lesson_valid = "Topic cannot be empty"
        else:
            generate_speaking_lesson(topic, level)
    _question = st.session_state.creating_lesson_data.get("questions", None)
    _main_question_value = ""
    _num_guidelines = 3
    _guidelines = ["" for _ in range(3)]
    if _question and isinstance(_question, dict):
        _main_question_value = _question.get("main_question", "")
        _num_guidelines = len(_question.get("guidelines", [_ for _ in range(3)]))
        _guidelines = _question.get("guidelines", ["" for _ in range(3)])
    main_question = st.text_input(
        "Main question",
        key="speaking_main_question",
        value=_main_question_value,
        placeholder=_main_question_value,
    )

    if main_question == "":
        st.session_state.creating_lesson_valid = "Main question cannot be empty"

    num_guidelines = st.select_slider(
        "Number of guidelines",
        options=[i for i in range(1, 6)],
        key="speaking_num_guidelines",
        value=_num_guidelines,
    )
    guidelines = []
    for i in range(num_guidelines):
        _guideline_value = _guidelines[i] if i < len(_guidelines) else ""
        guideline = st.text_input(
            f"Guideline {i + 1}",
            key=f"speaking_guideline_{i}",
            value=_guideline_value,
            placeholder=_guideline_value,
        )
        if guideline == "":
            st.session_state.creating_lesson_valid = "Guideline cannot be empty"
        guidelines.append(guideline)

    st.session_state.creating_lesson_data["questions"] = {
        "main_question": main_question,
        "guidelines": guidelines,
    }

    print(st.session_state.creating_lesson_data)

    summitted = st.button("Submit", key="speaking_submit")
    if summitted:
        if st.session_state.creating_lesson_valid == "ok":
            with get_httpx_client() as client:
                resp = client.post(
                    f"{get_settings().connection.backend_url.unicode_string()}lesson/v1/upload",
                    json={
                        "data": {
                            "authorId": st.session_state.user_info.id,
                            "name": name,
                            "description": description,
                            "type": lesson_type,
                            "level": parse_level_inv(level),
                            "content": {
                                "topic": topic,
                                "main_question": st.session_state.creating_lesson_data["questions"]["main_question"],  # type: ignore
                                "guidelines": st.session_state.creating_lesson_data[
                                    "questions"
                                ][
                                    "guidelines"
                                ],  # type: ignore
                            },
                        },
                    },
                )
                if resp.status_code != 200:
                    st.error("Failed to upload")
                    print(resp.text)
                else:
                    st.session_state.creating_lesson_data_finished = True
                    st.session_state.creating_lesson_info = {
                        "name": name,
                        "description": description,
                        "type": lesson_type,
                        "level": level,
                    }
                    st.success("Uploaded successfully")
                    st.switch_page("pages/display.py")

        else:
            st.error(st.session_state.creating_lesson_valid)
