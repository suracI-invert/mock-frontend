import streamlit as st
from utils.network import get_httpx_client
from components.lesson import Lesson
from components.lesson import LessonType
from components.lessons.exercise import do_exercise
from settings import get_settings


do_exercise()
