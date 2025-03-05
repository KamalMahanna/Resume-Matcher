import json
import os.path
import pathlib

from .parsers import ParseJobDesc, ParseResume

SAVE_DIRECTORY = "Data/Processed/JobDescription"


class JobDescriptionProcessor:
    def __init__(self, input_file):
        self.input_file = input_file
        self.raw_text = None  # Expect raw text to be passed directly

    def process(self) -> dict:  # Changed return type to dict
        try:
            jd_dict = self._read_job_desc()
            # self._write_json_file(jd_dict)  # No longer writing to file
            return jd_dict  # Return processed data
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return {}  # Return empty dict on error

    def _read_job_desc(self) -> dict:
        output = ParseJobDesc(self.raw_text).get_JSON()  # Pass raw text directly
        return output

    def _write_json_file(self, jd_dictionary: dict):
        file_name = str(
            "JobDescription-" + self.input_file + jd_dictionary["unique_id"] + ".json"
        )
        save_directory_name = pathlib.Path(SAVE_DIRECTORY) / file_name
        json_object = json.dumps(jd_dictionary, sort_keys=True, indent=14)
        with open(save_directory_name, "w+") as outfile:
            outfile.write(json_object)
