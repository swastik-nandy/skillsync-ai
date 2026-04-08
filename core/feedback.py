import re
import json
import tempfile
import subprocess
from typing import Dict


# ----------------- JSON Extraction Helper -----------------
def extract_json_block(text: str):
    """Safely extract and parse JSON from model output."""
    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        return {"raw_output": text.strip()}

    json_str = match.group(0)
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        cleaned = re.sub(r"(\w+):", r'"\1":', json_str)
        try:
            return json.loads(cleaned)
        except Exception:
            return {"raw_output": text.strip()}


# ----------------- Feedback Generator -----------------
def generate_feedback(state: Dict, llm=None):
    """
    Generate structured bullet-point resume feedback.
    Uses an external subprocess for GPU safety if Phi3-mini/TinyLlama is loaded.
    """
    print("🧠 Generating structured feedback ...")

    resume_text = state.get("resume_text", "")[:2500]
    jd_text = state.get("jd_text", "")[:2500]

    # ----------------- Prompt -----------------
    prompt = f"""
You are a senior AI recruiter evaluating a resume against a job description.
Your job is to give constructive, actionable feedback as JSON — no explanations, no text outside JSON.

Job Description:
{jd_text}

Resume (summary):
{resume_text}

Return only one valid JSON in this exact format:
{{
  "key_strengths": [
    "• Clear and specific strength #1",
    "• Clear and specific strength #2"
  ],
  "areas_of_improvement": [
    "• Specific weakness or missing skill #1",
    "• Specific weakness or missing skill #2"
  ],
  "recommendations": [
    "• Concrete next step or resource suggestion #1",
    "• Concrete next step or resource suggestion #2"
  ]
}}
Output only JSON — nothing else.
"""

    # ----------------- Write prompt to temporary file -----------------
    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp:
        tmp.write(prompt.encode("utf-8"))
        tmp_path = tmp.name

    # ----------------- Run a subprocess to prevent GPU OOM issues -----------------
    cmd = [
        "python3",
        "-c",
        (
            "from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline; "
            "import torch, re, json; "
            "model = AutoModelForCausalLM.from_pretrained('./core/models/tinyllama-1b', "
            "device_map='auto', local_files_only=True, torch_dtype=torch.float16); "
            "tok = AutoTokenizer.from_pretrained('./core/models/tinyllama-1b', local_files_only=True); "
            "pipe = pipeline('text-generation', model=model, tokenizer=tok, "
            "max_new_tokens=1024, temperature=0.6, do_sample=False); "
            f"prompt=open('{tmp_path}').read(); "
            "out = pipe(prompt)[0]['generated_text']; "
            "m = re.search(r'\\{[\\s\\S]*\\}', out); "
            "print(m.group(0) if m else out.strip())"
        ),
    ]

    try:
        output = subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL)
    except Exception as e:
        print("❌ Feedback subprocess failed:", e)
        state["feedback"] = {"error": str(e)}
        return state

    # ----------------- Clean output -----------------
    feedback_text = output.strip()
    print("\n🧩 Raw feedback output preview:\n", feedback_text[:600], "\n")

    # ----------------- Parse JSON -----------------
    feedback_json = extract_json_block(feedback_text)
    state["feedback"] = feedback_json

    return state
