import json
import os
from typing import List

import networkx as nx
import nltk
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from annotated_text import annotated_text, parameters
from streamlit_extras import add_vertical_space as avs
from streamlit_extras.badges import badge

from scripts.similarity.get_score import *
from scripts.utils import get_filenames_from_dir
from scripts.utils.logger import init_logging_config
from scripts.file_processor import process_all_files, reset_all
from scripts.visualizations import create_star_graph, create_annotated_text

# Set page configuration
st.set_page_config(
    page_title="Resume Matcher",
    page_icon="Assets/img/favicon.ico",
    initial_sidebar_state="auto",
)

init_logging_config()
cwd = find_path("resume-matcher")
config_path = os.path.join(cwd, "scripts", "similarity")

try:
    nltk.data.find("tokenizers/punkt_tab")
except LookupError:
    nltk.download("punkt_tab")

parameters.SHOW_LABEL_SEPARATOR = False
parameters.BORDER_RADIUS = 3
parameters.PADDING = "0.5 0.25rem"

def read_json(filename):
    with open(filename) as f:
        data = json.load(f)
    return data

def tokenize_string(input_string):
    tokens = nltk.word_tokenize(input_string)
    return tokens

# Initialize session state
if 'processing_complete' not in st.session_state:
    st.session_state.processing_complete = False

# Initialize sidebar
with st.sidebar:
    st.image("Assets/img/header_image.png")
    st.subheader(
        "Free and Open Source ATS to help your resume pass the screening stage."
    )
    st.markdown(
        "Check the website [www.resumematcher.fyi](https://www.resumematcher.fyi/)"
    )
    st.markdown(
        "Give Resume Matcher a ⭐ on [GitHub](https://github.com/srbhr/resume-matcher)"
    )
    badge(type="github", name="srbhr/Resume-Matcher")
    st.markdown("For updates follow me on Twitter.")
    badge(type="twitter", name="_srbhr_")
    st.markdown(
        "If you like the project and would like to further help in development please consider 👇"
    )
    badge(type="buymeacoffee", name="srbhr")

st.title(":blue[Resume Matcher]")

# File upload sections

col1, col2 = st.columns(2)
with col1:
    st.markdown("#### Upload Resumes (PDF)")
    uploaded_resumes = st.file_uploader("Choose PDF files", type="pdf", accept_multiple_files=True, key="resumes")
    if uploaded_resumes:
        st.session_state.uploaded_resumes = uploaded_resumes

with col2:
    st.markdown("#### Enter Job Description (Text)")
    job_description_text = st.text_area("Paste job description text here", height=300, key="jd_text")

# Process button
if st.button("Process All Files"):
    if not st.session_state.get("uploaded_resumes") or not st.session_state.get("jd_text"):
        st.error("Please upload at least one resume and provide a job description.")
    else:
        with st.spinner("Processing files..."):
            success = process_all_files(st.session_state.get("uploaded_resumes", []), st.session_state.get("jd_text", ""))
            if success:
                st.success("All files processed successfully!")
                st.session_state.processing_complete = True
            else:
                st.error("Error processing files. Please check the logs.")
                st.session_state.processing_complete = False
        st.rerun()

st.divider()
avs.add_vertical_space(1)

if st.session_state.processing_complete:
    if "processed_resumes" in st.session_state and st.session_state.processed_resumes:
        resume_names = list(st.session_state.processed_resumes.keys())
    else:
        resume_names = []

    st.markdown(
        f"##### There are {len(resume_names)} resumes present. Please select one from the menu below:"
    )
    output = st.selectbox(f"", resume_names)

    avs.add_vertical_space(5)

    selected_file = st.session_state.processed_resumes[output]

    avs.add_vertical_space(2)
    st.markdown("#### Parsed Resume Data")
    st.caption(
        "This text is parsed from your resume. This is how it'll look like after getting parsed by an ATS."
    )
    st.caption("Utilize this to understand how to make your resume ATS friendly.")
    avs.add_vertical_space(3)
    # st.json(selected_file)
    st.write(selected_file["clean_data"])

    avs.add_vertical_space(3)
    st.write("Now let's take a look at the extracted keywords from the resume.")

    annotated_text(
        create_annotated_text(
            selected_file["clean_data"],
            selected_file["extracted_keywords"],
            "KW",
            "#0B666A",
        )
    )

    avs.add_vertical_space(5)
    st.write("Now let's take a look at the extracted entities from the resume.")

    # Call the function with your data
    create_star_graph(selected_file["keyterms"], "Entities from Resume")

    df2 = pd.DataFrame(selected_file["keyterms"], columns=["keyword", "value"])

    # Create the dictionary
    keyword_dict = {}
    for keyword, value in selected_file["keyterms"]:
        keyword_dict[keyword] = value * 100

    fig = go.Figure(
        data=[
            go.Table(
                header=dict(
                    values=["Keyword", "Value"], font=dict(size=12), fill_color="#070A52"
                ),
                cells=dict(
                    values=[list(keyword_dict.keys()), list(keyword_dict.values())],
                    line_color="darkslategray",
                    fill_color="#6DA9E4",
                ),
            )
        ]
    )
    st.plotly_chart(fig)

    st.divider()

    fig = px.treemap(
        df2,
        path=["keyword"],
        values="value",
        color_continuous_scale="Rainbow",
        title="Key Terms/Topics Extracted from your Resume",
    )
    st.write(fig)

    avs.add_vertical_space(3)

    if "processed_jds" in st.session_state and st.session_state.processed_jds:
        selected_jd = st.session_state.processed_jds["job_description"]

        avs.add_vertical_space(2)
        st.markdown("#### Job Description")
        st.caption(
            "Currently in the pipeline I'm parsing this from PDF but it'll be from txt or copy paste."
        )
        avs.add_vertical_space(3)
        # st.json(selected_file)
        st.write(selected_jd["clean_data"])

        st.markdown("#### Common Words between Job Description and Resumes Highlighted.")

        annotated_text(
            create_annotated_text(
                selected_file["clean_data"], selected_jd["extracted_keywords"], "JD", "#F24C3D"
            )
        )

        st.write("Now let's take a look at the extracted entities from the job description.")

        # Call the function with your data
        create_star_graph(selected_jd["keyterms"], "Entities from Job Description")

        df2 = pd.DataFrame(selected_jd["keyterms"], columns=["keyword", "value"])

        # Create the dictionary
        keyword_dict = {}
        for keyword, value in selected_jd["keyterms"]:
            keyword_dict[keyword] = value * 100

        fig = go.Figure(
            data=[
                go.Table(
                    header=dict(
                        values=["Keyword", "Value"], font=dict(size=12), fill_color="#070A52"
                    ),
                    cells=dict(
                        values=[list(keyword_dict.keys()), list(keyword_dict.values())],
                        line_color="darkslategray",
                        fill_color="#6DA9E4",
                    ),
                )
            ]
        )
        st.plotly_chart(fig)

        st.divider()

        fig = px.treemap(
            df2,
            path=["keyword"],
            values="value",
            color_continuous_scale="Rainbow",
            title="Key Terms/Topics Extracted from the selected Job Description",
        )
        st.write(fig)

        avs.add_vertical_space(3)

        resume_string = " ".join(selected_file["extracted_keywords"])
        jd_string = " ".join(selected_jd["extracted_keywords"])
        result = get_score(resume_string, jd_string)
        similarity_score = round(result[0].score * 100, 2)
        score_color = "green"
        if similarity_score < 60:
            score_color = "red"
        elif 60 <= similarity_score < 75:
            score_color = "orange"
        st.markdown(
            f"Similarity Score obtained for the resume and job description is "
            f'<span style="color:{score_color};font-size:24px; font-weight:Bold">{similarity_score}</span>',
            unsafe_allow_html=True,
        )
    else:
        st.warning("Please click 'Process All Files' button above to analyze your documents.")

# Go back to top
st.markdown("[:arrow_up: Back to Top](#resume-matcher)")

# Add Reset button at the bottom if processing is complete
if st.session_state.processing_complete:
    st.divider()
    avs.add_vertical_space(2)
    if st.button("Reset All"):
        with st.spinner("Resetting..."):
            if reset_all():
                st.success("Reset complete!")
                st.session_state.processing_complete = False
                st.rerun()
            else:
                st.error("Error resetting files. Please check the logs.")
