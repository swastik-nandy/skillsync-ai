import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

res = genai.embed_content(
    model="models/gemini-embedding-001",
    content="test"
)

embedding = res["embedding"]
print("Embedding dimension:", len(embedding))