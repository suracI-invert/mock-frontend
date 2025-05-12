from datetime import datetime
from typing import Annotated
from pydantic import BaseModel, field_validator, ValidationInfo, BeforeValidator
from enum import Enum

from .user import UserInfo
from utils.validate import validate_datetime_format


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


class MultipleChoicesQuestion(BaseModel):
    index: int
    question: str
    answers: list[str]
    correct_answer: int


class SpeakingLessonContent(BaseModel):
    topic: str
    main_question: str
    guidelines: list[str]


class ListeningLessonContent(BaseModel):
    transcript: str
    audio_url: str = ""
    questions: list[MultipleChoicesQuestion]


class ReadingLessonContent(BaseModel):
    text: str
    questions: list[MultipleChoicesQuestion]


LessonContent = SpeakingLessonContent | ListeningLessonContent | ReadingLessonContent


class Lesson(BaseModel):
    id: int
    name: str
    description: str
    type: LessonType
    level: Level
    author: UserInfo
    createdAt: Annotated[
        datetime,
        BeforeValidator(validate_datetime_format),
    ]
    content: ReadingLessonContent | ListeningLessonContent | SpeakingLessonContent

    @field_validator("content", mode="plain")
    def set_content_validation_model(v, validation_info: ValidationInfo):
        vals = validation_info.data
        match vals["type"]:
            case LessonType.READING:
                return ReadingLessonContent.model_validate(v)
            case LessonType.LISTENING:
                return ListeningLessonContent.model_validate(v)
            case LessonType.SPEAKING:
                return SpeakingLessonContent.model_validate(v)
            case _:
                raise ValueError(f"Invalid lesson type: {vals['type']}")
