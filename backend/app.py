"""FastAPI application setup. Start with: uvicorn app:app --reload."""
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

from api import analysis, assessments, documents

app = FastAPI(
    title='SkillSync AI',
    description='Resume and job description analysis using hybrid retrieval and Groq.',
    version='0.1.0',
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=False,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.get('/health')
def health() -> dict:
    return {'status': 'ok', 'service': 'skillsync-ai'}


app.include_router(analysis.router)
app.include_router(documents.router)
app.include_router(assessments.router)

@app.get("/analysis/{analysis_id}/wait")
async def wait_for_analysis(
    analysis_id: str,
):
    import asyncio

    while True:
        snapshot = get_analysis(
            analysis_id,
        )

        if snapshot is None:
            raise HTTPException(
                status_code=404,
                detail="Analysis not found",
            )

        if snapshot.status in {
            "completed",
            "completed_with_errors",
        }:
            return RedirectResponse(
                url=(
                    "http://localhost:5173"
                    f"/report?analysis={analysis_id}"
                ),
                status_code=302,
            )

        if snapshot.status == "failed":
            return RedirectResponse(
                url=(
                    "http://localhost:5173"
                    f"/report?analysis={analysis_id}"
                    "&failed=1"
                ),
                status_code=302,
            )

        await asyncio.sleep(
            0.25,
        )

