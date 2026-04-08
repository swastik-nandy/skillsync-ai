import io
import fitz  # PyMuPDF
from docx import Document as DocxDocument
from .utils import clean_text

def extract_text(file_bytes: bytes, filename: str) -> str:
    """Extract text from PDF, DOCX, or plain text."""
    if filename.lower().endswith(".pdf"):
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        text = " ".join([page.get_text() for page in doc])
    elif filename.lower().endswith(".docx"):
        doc = DocxDocument(io.BytesIO(file_bytes))
        text = " ".join([p.text for p in doc.paragraphs])
    else:
        text = file_bytes.decode("utf-8", errors="ignore")

    return clean_text(text)
