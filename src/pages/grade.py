import streamlit as st

from components.exercise import grade

if "exercise_lesson" not in st.session_state:
    st.switch_page("/pages/lesson.py")
else:
    st.title("Result")
    st.write("---")
    data = st.session_state.exercise_lesson.get("final_data", None)
    if not data:
        st.switch_page("pages/lesson.py")
    else:
        grade(**data)
        back_btn = st.button("Back", key="grade_back")
        if back_btn:
            st.session_state.pop("exercise_lesson", None)
            st.switch_page("pages/lesson.py")
