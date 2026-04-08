import re
from core.extractor import extract_text
from core.analyzer import run_rag_analysis


# ---------------------------------------------------------------
# 🧩 Process Resume (text input)
# ---------------------------------------------------------------
def process_resume_local(resume_text: str, jd_text: str) -> dict:
    """
    Full resume-JD analysis pipeline using RAG + Groq LLM.
    """
    print("🚀 Starting RAG resume analysis (Groq)...")

    # Split resume into smaller chunks
    resume_chunks = _chunk_text(resume_text)

    # Run RAG pipeline (now uses Groq internally)
    result = run_rag_analysis(resume_chunks, jd_text)

    print("✅ RAG analysis complete.")

    raw_output = result.get("raw_output", "")

    return {
        "analysis": result,
        "feedback": _parse_feedback(raw_output),
    }


# ---------------------------------------------------------------
# 🧾 Process Resume File (PDF/DOCX)
# ---------------------------------------------------------------
def process_resume_file(file_bytes: bytes, filename: str, jd_text: str) -> dict:
    """
    Extract text from uploaded file and run full analysis pipeline.
    """
    print(f"📄 Extracting text from {filename} ...")
    resume_text = extract_text(file_bytes, filename)

    return process_resume_local(resume_text, jd_text)


# ---------------------------------------------------------------
# ✂️ Utility: Chunk Long Texts
# ---------------------------------------------------------------
def _chunk_text(text: str, max_words: int = 120):
    """
    Splits long text into smaller chunks for embedding and retrieval.
    """
    words = text.split()
    chunks = [
        " ".join(words[i:i + max_words])
        for i in range(0, len(words), max_words)
    ]
    print(f"🔹 Split resume into {len(chunks)} chunks.")
    return chunks


# ---------------------------------------------------------------
# 🧠 Parse Feedback from LLM Output (Groq-safe)
# ---------------------------------------------------------------
def _parse_feedback(text: str) -> dict:
    """
    Extract structured data from LLM output.
    Works with less predictable Groq responses.
    """

    # Match percentage (more flexible)
    match = re.search(r"(\d{1,3})\s?%?", text)
    match_percentage = match.group(1) if match else "N/A"

    return {
        "match_percentage": match_percentage,
        "strengths": _extract_section(text, ["strength", "advantage", "good"], ["weakness", "gap", "missing"]),
        "weaknesses": _extract_section(text, ["weakness", "gap", "missing"], ["suggest", "recommend"]),
        "suggestions": _extract_section(text, ["suggest", "recommend", "improve"], ["$", "conclusion"]),
    }


# ---------------------------------------------------------------
# 📍 Helper to Extract Text Between Keywords
# ---------------------------------------------------------------
def _extract_section(text, start_keywords, end_keywords):
    pattern_start = "|".join(start_keywords)
    pattern_end = "|".join(end_keywords)

    regex = rf"({pattern_start}).*?(?=({pattern_end})|$)"
    match = re.search(regex, text, re.IGNORECASE | re.DOTALL)

    return match.group(0).strip() if match else ""