from core.analyzer import run_rag_analysis
from core.extractor import extract_text
from core.schemas import FeedbackReport


# --------------- CHUNKING ---------------

def chunk_text(
    text: str,
    max_words: int = 120,
) -> list[str]:
    words = text.split()

    return [
        " ".join(words[i:i + max_words])
        for i in range(0, len(words), max_words)
    ]


# --------------- TEXT ANALYSIS ---------------

def process_resume_local(
    resume_text: str,
    jd_text: str,
) -> FeedbackReport:
    resume_chunks = chunk_text(
        resume_text
    )

    if not resume_chunks:
        raise ValueError(
            "Resume contains no readable text"
        )

    return run_rag_analysis(
        resume_chunks,
        jd_text,
    )


# --------------- FILE ANALYSIS ---------------

def process_resume_file(
    file_bytes: bytes,
    filename: str,
    jd_text: str,
) -> FeedbackReport:
    resume_text = extract_text(
        file_bytes,
        filename,
    )

    return process_resume_local(
        resume_text,
        jd_text,
    )
