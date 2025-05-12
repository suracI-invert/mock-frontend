import streamlit as st


def display_error():
    st.title("Error")
    st.write("---")
    st.write("Sorry, something went wrong. Please check in later :cry:")
    st.write("---")
    st.write("If you think this is a bug, please report it to us.")

    _, c2, _ = st.columns([1, 3, 1])
    with c2:
        ext_btn = st.button("Back to home")
        if ext_btn:
            st.switch_page("pages/home.py")


display_error()
