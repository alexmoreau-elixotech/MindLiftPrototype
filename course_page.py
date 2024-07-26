import streamlit as st
import os
import json
from utils import load_content

def CoursePage(course_name):
    chapters = load_content(f"./courses/{course_name}/course_chapters.json")

    for keys in chapters:
        with st.expander(chapters[keys]["title"]):
            sections = load_content(f"./courses/{course_name}/{keys}/sections.json")
            
            for sec in sections:
                st.header(sections[sec]["title"])
                subsections = load_content(f"./courses/{course_name}/{keys}/{sec}/content.json")
                for item in subsections:
                    if item["type"] == "text":
                        st.markdown(item["content"])
                    else:
                        st.latex(item["content"])
