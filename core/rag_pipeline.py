import os
import re
from typing import Dict, Union
from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

from core.llm import generate_with_groq  # 👈 NEW


# ----------------- Utility -----------------
def clean_text(text: Union[str, bytes]) -> str:
    text = text.decode("utf-8", errors="ignore") if isinstance(text, bytes) else text
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# ----------------- Structured Parser -----------------
schemas = [
    ResponseSchema(name="match_percentage", description="Number 0-100"),
    ResponseSchema(name="present_skills", description="List of matched skills"),
    ResponseSchema(name="missing_skills", description="List of missing skills"),
    ResponseSchema(name="improvements", description="Bullet point suggestions"),
]
parser = StructuredOutputParser.from_response_schemas(schemas)
format_instructions = parser.get_format_instructions()


# ----------------- Embedder -----------------
def get_local_embedder(local_path: str):
    print(f"🔹 Loading local embedder from: {local_path}")
    return HuggingFaceEmbeddings(model_name=local_path, cache_folder=local_path)


# ----------------- Pipeline Steps -----------------
def parse_inputs(state: Dict) -> Dict:
    state["resume_text"] = clean_text(state["resume_text"])
    state["jd_text"] = clean_text(state["jd_text"])
    return state


def build_vectorstore(state: Dict, embedder: HuggingFaceEmbeddings) -> Dict:
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_text(state["resume_text"])
    docs = [Document(page_content=c, metadata={"source": "resume"}) for c in chunks]
    state["vectorstore"] = FAISS.from_documents(docs, embedder)
    return state


def retrieve_relevant(state: Dict) -> Dict:
    retriever = state["vectorstore"].as_retriever(search_type="similarity", search_kwargs={"k": 5})
    docs = retriever.get_relevant_documents(state["jd_text"])
    state["retrieved_docs"] = docs or [Document(page_content=state["resume_text"])]
    return state


# ----------------- 🔥 GROQ ANALYSIS -----------------
def analyze_match(state: Dict) -> Dict:
    context = "\n\n".join([d.page_content for d in state["retrieved_docs"]])

    prompt = f"""
You are a resume analyzer.

Job Description:
{state['jd_text']}

Resume Extracts:
{context}

Follow this format strictly:
{format_instructions}
"""

    response = generate_with_groq(prompt)  # 👈 GROQ CALL

    try:
        parsed = parser.parse(response)
    except Exception:
        parsed = {"raw_output": response}

    state["analysis"] = parsed
    return state


# ----------------- Orchestrator -----------------
def process_resume_local(resume_text: str, jd_text: str, embed_dir: str) -> Dict:
    """End-to-end resume analysis using Groq LLM + local embeddings."""
    embedder = get_local_embedder(embed_dir)

    state = {"resume_text": resume_text, "jd_text": jd_text}

    for fn in [parse_inputs, build_vectorstore, retrieve_relevant]:
        state = fn(state, embedder) if "embedder" in fn.__code__.co_varnames else fn(state)

    state = analyze_match(state)

    return state["analysis"]