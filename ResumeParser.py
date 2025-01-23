from typing import BinaryIO
from pdf2image import convert_from_path
import os
import pdfplumber
import docx2txt
import json
import pytesseract


from GeminiAI import GeminiAI

class ResumeParser:

    @classmethod
    def __init__(cls, gemini_ai: GeminiAI):
        cls.gemini_ai = gemini_ai

    @classmethod
    def extract_text_from_pdf(cls, file):
        text = ""
        try:
            with pdfplumber.open(file) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                    else:
                        # if pdf belong to scan image => convert to text
                        images = convert_from_path(file, first_page=page.page_number, last_page=page.page_number)
                        for image in images:
                            page_text = pytesseract.image_to_string(image)
                            text += page_text + "\n"
        
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")

        return text

    @classmethod
    def extract_text_from_docx(cls, file):
        text = ""
        try:
            text = docx2txt.process(file)
        except Exception as e:
            print(f"Error extracting text from DOCX: {e}")
        return text

    @classmethod
    def to_json(cls, text_explanation):
        try:
            clean_explanation = text_explanation.replace("```json\n", "").replace("```", "")
            return json.loads(clean_explanation)
        except json.JSONDecodeError:
            print("Error decoding JSON")
            return None

    @classmethod
    def extract_content_by_extension(cls, binary: BinaryIO):
        file_extension = os.path.splitext(binary.name)[1]
        if file_extension == ".pdf":
            text = cls.extract_text_from_pdf(binary)
        elif file_extension == ".docx":
            text = cls.extract_text_from_docx(binary)
        else:
            print("Unsupported file format")
            return None

        return text

    @classmethod
    def parse_resume(cls, path: str):
        try:
            with open(path, "rb") as file_open:
                return cls.parse_resume_with_file(file_open)
        except FileNotFoundError:
            print("File not found")
            return None

    @classmethod
    def parse_resume_with_file(cls, binary: BinaryIO):
        text = cls.extract_content_by_extension(binary)
        if not text:
            return None

        text_explanation = cls.gemini_ai.explain_resume(text)
        json_explanation = cls.to_json(text_explanation)
        return json_explanation