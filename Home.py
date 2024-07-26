import streamlit as st
import os
from AI_connector import AI_connector
from utils import write_dict_to_file, write_list_to_file

def Home():
    st.set_page_config(
        page_title="Home"
    )

    conn = AI_connector()

    available_courses = os.listdir("./courses")

    st.title("Course generator prototype")

    def generate_course(subject):
        chapters = conn.generate_course_chapters(subject)
        os.makedirs(f"./courses/{subject}", exist_ok=True)

        write_dict_to_file(f"./courses/{subject}/course_chapters.json", chapters)

        sections = conn.generate_sections(chapters)

        for keys in sections:
            os.makedirs(f"./courses/{subject}/{keys}", exist_ok=True)
            write_dict_to_file(f"./courses/{subject}/{keys}/sections.json", sections[keys])
            for sec in sections[keys]:
                subsection = conn.generate_subsections(sections[keys][sec])
                os.makedirs(f"./courses/{subject}/{keys}/{sec}", exist_ok=True)
                write_list_to_file(f"./courses/{subject}/{keys}/{sec}/content.json", subsection)

        available_courses.append(subject)

    with st.form("course_builder"):
        course_subject = st.text_input("What do you want to learn?", "")
        submitted = st.form_submit_button("Generate course")

        if submitted:
            generate_course(course_subject)

    for elem in available_courses:
        if st.button(elem):
            st.session_state['selected_course'] = elem
            st.experimental_rerun()