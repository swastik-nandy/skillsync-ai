import re

import faiss
import numpy as np
from rank_bm25 import BM25Okapi

from core.embedder import embed_texts
from core.llm import generate_feedback
from core.prompts import load_prompt
from core.schemas import FeedbackReport


# --------------- TOKENIZATION ---------------

def tokenize(text: str) -> list[str]:
    return re.findall(r"\b\w+\b", text.lower())


# --------------- VECTOR SEARCH ---------------

def vector_scores(
    resume_embeddings: np.ndarray,
    jd_embedding: np.ndarray,
) -> np.ndarray:
    dimension = resume_embeddings.shape[1]

    index = faiss.IndexFlatIP(dimension)

    index.add(
        resume_embeddings.astype(np.float32)
    )

    scores, indices = index.search(
        jd_embedding.reshape(1, -1).astype(np.float32),
        len(resume_embeddings),
    )

    result = np.zeros(
        len(resume_embeddings),
        dtype=np.float32,
    )

    for score, index_position in zip(
        scores[0],
        indices[0],
    ):
        if index_position >= 0:
            result[index_position] = score

    return result


# --------------- BM25 SEARCH ---------------

def bm25_scores(
    resume_chunks: list[str],
    jd_text: str,
) -> np.ndarray:
    tokenized_chunks = [
        tokenize(chunk)
        for chunk in resume_chunks
    ]

    bm25 = BM25Okapi(
        tokenized_chunks
    )

    scores = bm25.get_scores(
        tokenize(jd_text)
    )

    return np.asarray(
        scores,
        dtype=np.float32,
    )


# --------------- SCORE NORMALIZATION ---------------

def normalize_scores(
    scores: np.ndarray,
) -> np.ndarray:
    minimum = scores.min()
    maximum = scores.max()

    if maximum == minimum:
        return np.zeros_like(scores)

    return (
        scores - minimum
    ) / (
        maximum - minimum
    )


# --------------- HYBRID SEARCH ---------------

def hybrid_search(
    resume_chunks: list[str],
    jd_text: str,
    top_k: int = 5,
    vector_weight: float = 0.7,
    bm25_weight: float = 0.3,
) -> list[str]:
    all_texts = resume_chunks + [jd_text]

    embeddings = embed_texts(
        all_texts
    )

    resume_embeddings = embeddings[:-1]
    jd_embedding = embeddings[-1]

    semantic = vector_scores(
        resume_embeddings,
        jd_embedding,
    )

    lexical = bm25_scores(
        resume_chunks,
        jd_text,
    )

    semantic = normalize_scores(
        semantic
    )

    lexical = normalize_scores(
        lexical
    )

    combined = (
        vector_weight * semantic
        + bm25_weight * lexical
    )

    top_k = min(
        top_k,
        len(resume_chunks),
    )

    ranked_indices = np.argsort(
        combined
    )[::-1][:top_k]

    return [
        resume_chunks[index]
        for index in ranked_indices
    ]


# --------------- FEEDBACK GENERATION ---------------

def analyze_match(
    resume_chunks: list[str],
    jd_text: str,
) -> FeedbackReport:
    prompt = load_prompt(
        "feedback_generation"
    )

    resume_context = "\n\n".join(
        resume_chunks
    )

    user_prompt = (
        prompt["user_prompt"]
        .replace("{jd_text}", jd_text)
        .replace("{resume_context}", resume_context)
    )

    return generate_feedback(
        system_prompt=prompt["system_prompt"],
        user_prompt=user_prompt,
    )


# --------------- RAG ANALYSIS ---------------

def run_rag_analysis(
    resume_chunks: list[str],
    jd_text: str,
) -> FeedbackReport:
    if not resume_chunks:
        raise ValueError(
            "Resume produced no text chunks"
        )

    top_chunks = hybrid_search(
        resume_chunks,
        jd_text,
    )

    return analyze_match(
        top_chunks,
        jd_text,
    )
