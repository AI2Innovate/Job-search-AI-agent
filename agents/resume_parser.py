# agents/resume_parser.py
from PyPDF2 import PdfReader
from docx import Document
import pandas as pd

def extract_text_from_pdf(file):
    reader = PdfReader(file)
    return "\n".join(page.extract_text() or "" for page in reader.pages)

def extract_text_from_docx(file):
    doc = Document(file)
    return "\n".join(para.text for para in doc.paragraphs)

def extract_keywords_from_text(text, max_lines=2):
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    return " ".join(lines[:max_lines])

def extract_keywords_from_csv(file, max_fields=2):
    df = pd.read_csv(file)
    if df.empty:
        return ""
    first = df.iloc[0]
    vals = [str(first[c]) for c in df.columns[:max_fields]]
    return " ".join(vals)
