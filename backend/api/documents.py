"""Local document parsing and diagnostics, with no LLM calls."""
import asyncio
from collections.abc import Callable

from fastapi import APIRouter, File, HTTPException, UploadFile

from core.resume_diagnostics import inspect_resume_diagnostics
from core.resume_parse_metrics import inspect_resume_parse
from core.schemas import ResumeDiagnosticsReport, ResumeParseReport

router = APIRouter()


async def inspect_upload(file: UploadFile, inspector: Callable):
    if not file.filename:
        raise HTTPException(status_code=400, detail='Resume filename is required.')
    file_bytes = await file.read()
    try:
        return await asyncio.to_thread(inspector, file_bytes, file.filename)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@router.post('/resume/parse', response_model=ResumeParseReport)
async def parse_resume(file: UploadFile = File(...)):
    return await inspect_upload(file, inspect_resume_parse)


@router.post('/resume/diagnostics', response_model=ResumeDiagnosticsReport)
async def resume_diagnostics(file: UploadFile = File(...)):
    return await inspect_upload(file, inspect_resume_diagnostics)
