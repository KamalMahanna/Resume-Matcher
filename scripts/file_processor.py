import json
import logging
import os
import shutil

from scripts import JobDescriptionProcessor, ResumeProcessor
from scripts.utils import get_filenames_from_dir, init_logging_config

init_logging_config()

def setup_directories():
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    processed_data_path = os.path.join(script_dir, "Data", "Processed")
    processed_resumes_path = os.path.join(processed_data_path, "Resumes")
    processed_jd_path = os.path.join(processed_data_path, "JobDescription")
    
    # Check if processed data directory exists
    if not os.path.exists(processed_data_path):
        os.makedirs(processed_data_path)
        os.makedirs(processed_resumes_path)
        os.makedirs(processed_jd_path)
        logging.info("Created necessary directories.")
        
    return processed_data_path, processed_resumes_path, processed_jd_path

def remove_directory_contents(directory):
    """Remove all files and subdirectories from the specified directory"""
    if not os.path.exists(directory):
        os.makedirs(directory)
        return
        
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            logging.error(f"Error deleting {file_path}:\n{e}")
            
    logging.info(f"Cleared contents of {directory}")

def process_resumes():
    """Process all resumes in the Data/Resumes directory"""
    try:
        _, processed_resumes_path, _ = setup_directories()
        remove_directory_contents(processed_resumes_path)
        
        file_names = get_filenames_from_dir("Data/Resumes")
        if not file_names:
            raise Exception("No resume files found")
            
        logging.info("Started parsing the resumes.")
        for file in file_names:
            processor = ResumeProcessor(file)
            success = processor.process()
        logging.info("Parsing of the resumes is now complete.")
        return True
        
    except Exception as e:
        logging.error(f"Error processing resumes: {str(e)}")
        return False

def process_job_descriptions():
    """Process all job descriptions in the Data/JobDescription directory"""
    try:
        _, _, processed_jd_path = setup_directories()
        remove_directory_contents(processed_jd_path)
        
        file_names = get_filenames_from_dir("Data/JobDescription")
        if not file_names:
            raise Exception("No job description files found")
            
        logging.info("Started parsing the Job Descriptions.")
        for file in file_names:
            processor = JobDescriptionProcessor(file)
            success = processor.process()
        logging.info("Parsing of the Job Descriptions is now complete.")
        return True
        
    except Exception as e:
        logging.error(f"Error processing job descriptions: {str(e)}")
        return False

def process_all_files():
    """Process both resumes and job descriptions"""
    resumes_success = process_resumes()
    jd_success = process_job_descriptions()
    return resumes_success and jd_success

def reset_all():
    """Reset the application by removing all uploaded and processed files"""
    try:
        # Clear uploaded files
        remove_directory_contents("Data/Resumes")
        remove_directory_contents("Data/JobDescription")
        
        # Clear processed files
        processed_data_path, _, _ = setup_directories()
        remove_directory_contents(processed_data_path)
        
        logging.info("Successfully reset all files")
        return True
    except Exception as e:
        logging.error(f"Error resetting files: {str(e)}")
        return False
