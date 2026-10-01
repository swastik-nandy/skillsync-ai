import io

import pymupdf
from docx import Document

from core.utils import clean_text


# --------------- PDF ---------------

def extract_pdf(file_bytes: bytes) -> str:
    with pymupdf.open(
        stream=file_bytes,
        filetype="pdf",
    ) as document:
        return " ".join(
            page.get_text()
            for page in document
        )


# --------------- DOCX ---------------

def extract_docx(file_bytes: bytes) -> str:
    document = Document(
        io.BytesIO(file_bytes)
    )

    return " ".join(
        paragraph.text
        for paragraph in document.paragraphs
    )


# --------------- TEXT ---------------

def extract_plain_text(file_bytes: bytes) -> str:
    return file_bytes.decode(
        "utf-8",
        errors="ignore",
    )


# --------------- EXTRACTION ---------------

def extract_text(
    file_bytes: bytes,
    filename: str,
) -> str:
    filename = filename.lower()

    if filename.endswith(".pdf"):
        text = extract_pdf(file_bytes)

    elif filename.endswith(".docx"):
        text = extract_docx(file_bytes)

    elif filename.endswith(".txt"):
        text = extract_plain_text(file_bytes)

    else:
        raise ValueError("Unsupported resume file type")

    return clean_text(text)
