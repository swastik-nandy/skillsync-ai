from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
import re, json

def generate_feedback_fallback(resume_text, jd_text):
    print("⚡ Using fallback feedback model (CPU-safe, guaranteed output)...")

    # --- tiny model just for short text generation ---
    model_id = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
    tok = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(model_id, device_map="auto")

    pipe = pipeline(
        "text-generation",
        model=model,
        tokenizer=tok,
        max_new_tokens=512,
        temperature=0.6,
        do_sample=False,
    )

    prompt = f"""
You are a recruiter reviewing a resume.
Return JSON only, like this:

{{
  "key_strengths": ["• concise bullet points"],
  "areas_of_improvement": ["• concise bullet points"],
  "recommendations": ["• concise bullet points"]
}}

Job Description: {jd_text}
Resume: {resume_text[:1500]}
"""

    out = pipe(prompt)[0]["generated_text"]
    match = re.search(r"\{[\s\S]*\}", out)
    text = match.group(0).strip() if match else out.strip()

    try:
        return json.loads(text)
    except Exception:
        return {"raw_output": text}
