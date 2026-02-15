from io import BytesIO

from docx import Document
from pypdf import PdfReader


def extract_text_from_upload(filename: str, content: bytes) -> str:
    lower = filename.lower()
    if lower.endswith('.txt'):
        return content.decode('utf-8', errors='ignore')
    if lower.endswith('.pdf'):
        reader = PdfReader(BytesIO(content))
        return '\n'.join(page.extract_text() or '' for page in reader.pages)
    if lower.endswith('.docx'):
        doc = Document(BytesIO(content))
        return '\n'.join(p.text for p in doc.paragraphs)
    raise ValueError('Unsupported file type')
