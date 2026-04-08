from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import sys
import os

# Add parent directory to path so we can import core
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.pipeline import process_resume_file

app = FastAPI(
    title="AI Resume Analyzer Backend",
    description="Backend service for analyzing resumes using Gemini + FAISS + MiniLM embeddings.",
    version="1.0.0"
)

# ------------------- CORS -------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------- Health Check -------------------
@app.get("/health")
def health():
    return {"status": "ok", "service": "resume-analyzer"}

# ------------------- Main Route -------------------
@app.post("/analyze")
async def analyze_resume(
    file: UploadFile = File(...),
    jd_text: str = Form(...)
):
    """
    Receives a resume file + job description,
    runs the AI pipeline (Gemini + FAISS), and returns structured analysis.
    """
    # Validate file extension
    allowed_extensions = ('.pdf', '.docx', '.txt')
    if not file.filename.lower().endswith(allowed_extensions):
        raise HTTPException(
            status_code=400,
            detail=f"Only {allowed_extensions} files allowed"
        )

    print(f"📄 Received file: {file.filename} ({file.content_type})")
    
    try:
        file_bytes = await file.read()
        
        # Run the core resume pipeline (Gemini version — 3 args only)
        result = process_resume_file(file_bytes, file.filename, jd_text)

        print("✅ Pipeline completed")
        
        # Extract data from result structure
        analysis = result.get("analysis", {})
        feedback = result.get("feedback", {})
        
        # Build response
        response_data = {
            "match_percentage": feedback.get("match_percentage", "N/A"),
            "strengths": feedback.get("strengths", "—"),
            "weaknesses": feedback.get("weaknesses", "—"),
            "suggestions": feedback.get("suggestions", "—"),
            "raw_output": analysis.get("raw_output", "")
        }

        return JSONResponse(content=response_data)

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )