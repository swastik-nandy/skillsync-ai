from sentence_transformers import SentenceTransformer
import torch

def get_local_embedder(embed_dir):
    """
    Loads MiniLM for embeddings on GPU if available.
    """
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"🔹 Loading MiniLM embedder on {device.upper()} ...")
    model = SentenceTransformer('all-MiniLM-L6-v2', device=device)
    return model
