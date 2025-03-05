import json
import logging
import os
import shutil
import streamlit as st

from scripts import JobDescriptionProcessor, ResumeProcessor
from scripts.utils import get_filenames_from_dir, init_logging_config

init_logging_config()


def process_resumes(uploaded_resumes):
    """Process uploaded resumes"""
    processed_resumes = {}
    if not uploaded_resumes:
        logging.warning("No resumes uploaded.")
        return False, processed_resumes

    logging.info("Started parsing the resumes.")
    for uploaded_file in uploaded_resumes:
        try:
            resume_processor = ResumeProcessor(uploaded_file.name)
            resume_processor.raw_text = uploaded_file.read() # Pass raw content (bytes)
            processed_data = resume_processor.process()
            if processed_data: # Check if processing was successful (dict not empty)
                processed_resumes[uploaded_file.name] = processed_data
                logging.info(f"Processed resume: {uploaded_file.name}")
            else:
                logging.error(f"Error processing resume {uploaded_file.name}: process() returned empty dict")
                return False, processed_resumes # Return False if processing failed
        except Exception as e:
            logging.error(f"Error processing resume {uploaded_file.name}: {e}")
            return False, processed_resumes

    logging.info("Parsing of the resumes is now complete.")
    return True, processed_resumes

def process_job_descriptions(jd_text):
    """Process job description text"""
    processed_jd = {}
    if not jd_text:
        logging.warning("No job description text provided.")
        return False, processed_jd

    logging.info("Started parsing the Job Description text.")
    try:
        jd_processor = JobDescriptionProcessor("job_description")
        jd_processor.raw_text = jd_text # Pass raw text
        processed_data = jd_processor.process()
        if processed_data: # Check if processing was successful
            processed_jd["job_description"] = processed_data
            logging.info(f"Processed job description text")
        else:
            logging.error(f"Error processing job description text: process() returned empty dict")
            return False, processed_jd # Return False if processing failed
    except Exception as e:
        logging.error(f"Error processing job description text: {e}")
        return False, processed_jd

    logging.info("Parsing of the Job Description is now complete.")
    return True, processed_jd

def process_all_files(uploaded_resumes, jd_text):
    """Process both resumes and job description from session state"""
    resumes_success, processed_resumes = process_resumes(uploaded_resumes)
    jd_success, processed_jd = process_job_descriptions(jd_text)

    if resumes_success and jd_success:
        st.session_state.processed_resumes = processed_resumes
        st.session_state.processed_jds = processed_jd
        return True
    else:
        return False

def reset_all():
    """Reset the application by clearing session state"""
    try:
        # Clear session state keys
        for key in ["uploaded_resumes", "jd_text", "processed_resumes", "processed_jds", "processing_complete"]:
            if key in st.session_state:
                del st.session_state[key]

        logging.info("Successfully reset all files")
        return True
    except Exception as e:
        logging.error(f"Error resetting files: {str(e)}")
        return False
