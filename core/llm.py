import os
from dotenv import load_dotenv
from groq import Groq


# ---------------------------------------------------------------
# 🔧 Load Environment & Configure Groq API
# ---------------------------------------------------------------
load_dotenv(dotenv_path="./core/.env")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
LLM_MODEL = os.getenv("LLM_MODEL", "llama3-70b-8192")  # default fallback

if not GROQ_API_KEY:
    raise ValueError("❌ GROQ_API_KEY not found in .env file (core/.env)")

client = Groq(api_key=GROQ_API_KEY)


# ---------------------------------------------------------------
# 🤖 Groq Model Wrapper
# ---------------------------------------------------------------
def get_groq_client():
    """
    Returns initialized Groq client.
    """
    return client


# ---------------------------------------------------------------
# 💬 Run Inference Helper (Groq)
# ---------------------------------------------------------------
def generate_with_groq(prompt: str):
    """
    Generate a text response using Groq LLM.
    Reads model from .env (LLM_MODEL).
    """

    try:
        print(f"🚀 Using Groq model: {LLM_MODEL}")

        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"❌ Groq API call failed: {e}")
        return f"[Groq Error] {str(e)}"