"""
PDF Extractor Module
Extracts raw text from uploaded PDF files using PyPDF2.
"""

import PyPDF2


def extract_text_from_pdf(file_path):
    """
    Reads a PDF file and returns all extracted text as a single string.
    Returns empty string if extraction fails.
    """
    try:
        text = ""
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text.strip()
    except Exception as e:
        print(f"[PDF Extractor] Error reading PDF: {e}")
        return ""
