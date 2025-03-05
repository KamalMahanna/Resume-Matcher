import json
import os.path
import pathlib

from .parsers import ParseJobDesc, ParseResume
from .ReadPdf import read_single_pdf

SAVE_DIRECTORY = "Data/Processed/Resumes"


class ResumeProcessor:
    def __init__(self, input_file):
        self.input_file = input_file
        self.raw_text = None # Expect raw text to be passed directly

    def process(self) -> dict: # Changed return type to dict to return processed data
        try:
            resume_dict = self._read_resumes()
            # self._write_json_file(resume_dict) # No longer writing to file
            return resume_dict # Return processed data
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return {} # Return empty dict on error

    def _read_resumes(self) -> dict:
        data = read_single_pdf(self.raw_text) # Pass raw text directly
        output = ParseResume(data).get_JSON()
        return output

    def _read_job_desc(self) -> dict:
        data = read_single_pdf(self.raw_text) # Pass raw text directly
        output = ParseJobDesc(data).get_JSON()
        return output

    def _write_json_file(self, resume_dictionary: dict):
        file_name = str(
            "Resume-" + self.input_file + resume_dictionary["unique_id"] + ".json"
        )
        save_directory_name = pathlib.Path(SAVE_DIRECTORY) / file_name
        json_object = json.dumps(resume_dictionary, sort_keys=True, indent=14)
        with open(save_directory_name, "w+") as outfile:
            outfile.write(json_object)
