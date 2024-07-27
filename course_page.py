import streamlit as st
import os
import json
from utils import load_content

def CoursePage(course_name):
    chapters = load_content(f"./courses/{course_name}/course_chapters.json")
    solution_checker = {}
    i = 0

    for keys in chapters:
        with st.expander("**"+chapters[keys]["title"]+"**"):
            sections = load_content(f"./courses/{course_name}/{keys}/sections.json")
            
            for sec in sections:
                subsections = load_content(f"./courses/{course_name}/{keys}/{sec}/content.json")
                for item in subsections:
                    if item["type"] == "text":
                        st.markdown(item["content"])
                    else:
                        st.latex(item["content"])

                st.markdown("# Exercises")
                math_exercises = load_content(f"./courses/{course_name}/{keys}/{sec}/math_problems.json")

                for m in math_exercises:
                    i += 1
                    st.markdown("## Problem")
                    st.markdown(m["problem"])
                    st.markdown("## Solution")

                    with st.form(f"math_problem_{i}"):
                        solution_checker[f"math_problem_{i}"] = {}

                        for v in m["solution"]:
                            solution_checker[f"math_problem_{i}"][v] = {
                                "solution": m["solution"][v] 
                            }

                            solution_checker[f"math_problem_{i}"][v]["answer"] = st.text_input(v)

                        submitted = st.form_submit_button("Check")

                        if submitted:
                            correct = True
                            for k in solution_checker[f"math_problem_{i}"]:
                                if solution_checker[f"math_problem_{i}"][k]["solution"] != solution_checker[f"math_problem_{i}"][k]["answer"]:
                                    correct = False

                            if not correct:
                                st.write("Solution is incorrect")
                            else:
                                st.write("Solution is correct!")
                    



