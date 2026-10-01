"""Full analysis submission and polling; both submission routes share one pipeline."""
import logging

from fastapi import APIRouter, BackgroundTasks, File, Form, HTTPException, UploadFile

from core.analysis_orchestrator import create_analysis, get_analysis, run_analysis
from core.analysis_schemas import AnalysisSnapshot, AnalysisStartResponse

router = APIRouter()
logger = logging.getLogger(__name__)
SUPPORTED_EXTENSIONS = ('.pdf', '.docx', '.txt')


def validate_analysis_input(file: UploadFile, jd_text: str) -> None:
    if not file.filename:
        raise HTTPException(status_code=400, detail='Resume filename is missing')
    if not file.filename.lower().endswith(SUPPORTED_EXTENSIONS):
        raise HTTPException(status_code=400, detail='Only PDF, DOCX, and TXT resumes are supported')
    if not jd_text.strip():
        raise HTTPException(status_code=400, detail='Job description cannot be empty')


@router.post('/analyze')
async def analyze_resume(file: UploadFile = File(...), jd_text: str = Form(...)):
    validate_analysis_input(file, jd_text)
    try:
        file_bytes = await file.read()
        analysis = create_analysis(file.filename)
        await run_analysis(analysis.analysis_id, file_bytes, file.filename, jd_text)
        snapshot = get_analysis(analysis.analysis_id)
        if snapshot.status == 'failed':
            raise RuntimeError(snapshot.sections['feedback'].error or 'Unable to analyze resume. Please retry.')
        return snapshot.sections['feedback'].result
    except ValueError as error:
        logger.exception('Resume analysis failed')
        raise HTTPException(status_code=400, detail=str(error)) from error
    except Exception as error:
        logger.exception('Resume analysis failed')
        raise HTTPException(status_code=500, detail=str(error)) from error


@router.post('/analysis/start', response_model=AnalysisStartResponse, status_code=202)
async def start_analysis(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    jd_text: str = Form(...),
):
    validate_analysis_input(file, jd_text)
    file_bytes = await file.read()
    analysis = create_analysis(file.filename)
    background_tasks.add_task(
        run_analysis, analysis.analysis_id, file_bytes, file.filename, jd_text,
    )
    return AnalysisStartResponse(analysis_id=analysis.analysis_id, status=analysis.status)


@router.get('/analysis/{analysis_id}', response_model=AnalysisSnapshot)
async def analysis_status(analysis_id: str):
    analysis = get_analysis(analysis_id)
    if analysis is None:
        raise HTTPException(status_code=404, detail='Analysis not found')
    return analysis
