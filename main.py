import streamlit as st
from Home import Home
from course_page import CoursePage

if 'selected_course' not in st.session_state:
    st.session_state['selected_course'] = None

if st.session_state['selected_course'] == None:
    Home()
else:
    CoursePage(st.session_state['selected_course'])