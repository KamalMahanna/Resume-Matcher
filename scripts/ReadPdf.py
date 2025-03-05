import glob
import os
import io

from pypdf import PdfReader


def read_multiple_pdf(pdf_contents) -> list:
    """
    Read multiple PDF contents and extract the text from each page.

    Args:
        pdf_contents (list): A list of PDF file contents (bytes).

    Returns:
        list: A list containing the extracted text from each page of the PDF files.
    """
    output = []
    for content in pdf_contents:
        try:
            pdf_reader = PdfReader(io.BytesIO(content)) # Wrap content in BytesIO
            count = pdf_reader.getNumPages()
            for i in range(count):
                page = pdf_reader.getPage(i)
                output.append(page.extractText())
        except Exception as e:
            print(f"Error reading PDF content: {str(e)}")
    return output


def read_single_pdf(pdf_content) -> str:
    """
    Read a single PDF content and extract the text from each page.

    Args:
        pdf_content (bytes): The content of the PDF file (bytes).

    Returns:
        str: A string containing the extracted text from the PDF file.
    """
    output = []
    try:
        pdf_reader = PdfReader(io.BytesIO(pdf_content)) # Wrap content in BytesIO
        count = len(pdf_reader.pages)
        for i in range(count):
            page = pdf_reader.pages[i]
            output.append(page.extract_text())
    except Exception as e:
        print(f"Error reading PDF content: {str(e)}")
    return str(" ".join(output))
