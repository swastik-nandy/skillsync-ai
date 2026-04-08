from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router

app = FastAPI(title="Resume Analyzer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")

@app.get("/health")
def health():
    return {"status": "ok"}