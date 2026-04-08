import numpy as np
import faiss
import torch
from sentence_transformers import SentenceTransformer
from core.llm import generate_with_groq


# ---------------------------------------------------------------
# 🔹 Build FAISS Index (auto GPU/CPU)
# ---------------------------------------------------------------
def build_faiss_index(embeddings: np.ndarray):
    """Build a FAISS index and use GPU if available."""
    dim = embeddings.shape[1]
    try:
        res = faiss.StandardGpuResources()
        index_flat = faiss.IndexFlatL2(dim)
        gpu_index = faiss.index_cpu_to_gpu(res, 0, index_flat)
        gpu_index.add(embeddings.astype("float32"))
        print("✅ Using FAISS GPU")
        return gpu_index
    except Exception as e:
        print(f"⚠️ GPU FAISS unavailable, using CPU fallback: {e}")
        index_flat = faiss.IndexFlatL2(dim)
        index_flat.add(embeddings.astype("float32"))
        return index_flat


# ---------------------------------------------------------------
# 🧩 Encode Resume & JD
# ---------------------------------------------------------------
def embed_texts(resume_chunks, jd_text, embed_model_name="all-MiniLM-L6-v2"):
    """Embed resume chunks + JD text using SentenceTransformer."""
    print("🔹 Loading embedder...")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = SentenceTransformer(embed_model_name, device=device)
    print(f"✅ Embedder loaded on {device.upper()}")

    # Create embeddings
    all_texts = resume_chunks + [jd_text]
    embeddings = model.encode(all_texts, show_progress_bar=True)
    return np.array(embeddings[:-1]), np.array(embeddings[-1])


# ---------------------------------------------------------------
# 🧠 Retrieve Top-K Relevant Chunks
# ---------------------------------------------------------------
def retrieve_top_chunks(index, resume_chunks, jd_embedding, top_k=5):
    """Retrieve most similar resume chunks to the JD."""
    jd_embedding = np.expand_dims(jd_embedding, axis=0).astype("float32")
    distances, indices = index.search(jd_embedding, top_k)
    top_texts = [resume_chunks[i] for i in indices[0] if i < len(resume_chunks)]
    print(f"📄 Retrieved top {len(top_texts)} relevant resume chunks.")
    return top_texts


# ---------------------------------------------------------------
# 💬 Gemini-powered Resume Analysis
# ---------------------------------------------------------------
def analyze_match(resume_chunks, jd_text):
    """
    Use Gemini to compare JD and retrieved resume chunks.
    Returns structured strengths, weaknesses, and suggestions.
    """
    context_text = "\n\n".join(resume_chunks)
    prompt = f"""
You are an experienced AI recruiter.

Compare the following resume content and job description.

Return a short, structured evaluation with:
- Match Percentage (0–100%)
- Key Strengths (skills or experiences that match)
- Weaknesses / Missing Skills
- Suggestions for improvement or alignment tips.

Be concise and professional.

=== JOB DESCRIPTION ===
{jd_text}

=== RESUME CONTEXT ===
{context_text}
"""

    response_text = generate_with_groq(prompt)
    print("\n🧠 Gemini raw output preview:\n", response_text[:500])
    return response_text


# ---------------------------------------------------------------
# 🧾 Main Orchestrator
# ---------------------------------------------------------------
def run_rag_analysis(resume_chunks, jd_text):
    """End-to-end RAG analysis combining embeddings + Gemini."""
    print("⚙️ Encoding resume chunks ...")
    resume_embeds, jd_embed = embed_texts(resume_chunks, jd_text)

    print("⚙️ Building FAISS index ...")
    index = build_faiss_index(resume_embeds)

    print("🔎 Retrieving top matches ...")
    top_chunks = retrieve_top_chunks(index, resume_chunks, jd_embed)

    print("🧠 Sending RAG context to Gemini ...")
    analysis_text = analyze_match(top_chunks, jd_text)

    # Simple parsing
    return {
        "match_percentage": _extract_match(analysis_text),
        "raw_output": analysis_text,
    }


# ---------------------------------------------------------------
# 🔍 Simple Percentage Parser
# ---------------------------------------------------------------
def _extract_match(text: str) -> str:
    """Extract numeric percentage if present."""
    import re
    match = re.search(r"(\d{1,3})\s?%", text)
    return match.group(1) if match else "N/A"
