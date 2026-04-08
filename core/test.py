from core.pipeline import process_resume_file

if __name__ == "__main__":
    with open("./samples/swastik_resume.pdf", "rb") as f:
        file_bytes = f.read()

    jd = "Looking for an AI Engineer with skills in Python, ML, LangChain, and RAG systems."

    result = process_resume_file(
        file_bytes=file_bytes,
        filename="swastik_resume.pdf",
        jd_text=jd,
        llm_dir="./models/phi3-mini",
        embed_dir="./models/all-MiniLM-L6-v2"
    )

    print("\n🧾 Skill Match:\n", result["analysis"])
    print("\n💬 Feedback:\n", result["feedback"])
