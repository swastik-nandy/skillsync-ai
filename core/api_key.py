import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load your .env
load_dotenv(dotenv_path="./core/.env")

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

print("\n🔍 Available Gemini Models:\n" + "-" * 40)
for model in genai.list_models():
    print(model.name)
