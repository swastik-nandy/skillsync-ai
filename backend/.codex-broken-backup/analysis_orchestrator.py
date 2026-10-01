"""Asynchronous analysis state around a single structured LLM request."""
import asyncio
import logging
from time import perf_counter
from uuid import uuid4

from core.analysis_schemas import AnalysisSectionState, AnalysisSnapshot
from core.analysis_errors import analysis_error_message, analysis_error_context
from core.extractor import extract_text
from core.resume_diagnostics import inspect_resume_diagnostics
from core.unified_analysis import generate_unified_analysis, assemble_sections

SECTION_NAMES = (
    "document_health",
    "feedback",
    "evidence_quality",
    "requirement_importance",
    "skills_alignment",
    "experience_fit",
    "qualification_alignment",
    "project_relevance",
    "overall_role_alignment",
)

_ANALYSES: dict[str, AnalysisSnapshot] = {}
_SECTION_STARTS: dict[tuple[str, str], float] = {}
logger = logging.getLogger(__name__)


# --------------- STATE HELPERS ---------------

def create_analysis(
    filename: str,
) -> AnalysisSnapshot:
    analysis_id = str(
        uuid4()
    )

    snapshot = AnalysisSnapshot(
        analysis_id=analysis_id,
        status="queued",
        filename=filename,
        finished_sections=0,
        total_sections=len(
            SECTION_NAMES
        ),
        sections={
            name: AnalysisSectionState()
            for name in SECTION_NAMES
        },
    )

    _ANALYSES[
        analysis_id
    ] = snapshot

    return snapshot.model_copy(
        deep=True
    )


def get_analysis(
    analysis_id: str,
) -> AnalysisSnapshot | None:
    snapshot = _ANALYSES.get(
        analysis_id
    )

    if snapshot is None:
        return None

    return snapshot.model_copy(
        deep=True
    )


def _refresh_finished_sections(
    snapshot: AnalysisSnapshot,
) -> None:
    terminal = {
        "completed",
        "failed",
        "skipped",
    }

    snapshot.finished_sections = sum(
        section.status in terminal
        for section in snapshot.sections.values()
    )


def _set_section(
    analysis_id: str,
    section_name: str,
    *,
    status: str,
    result: dict | None = None,
    error: str | None = None,
) -> None:
    snapshot = _ANALYSES[
        analysis_id
    ]

    timer_key = (analysis_id, section_name)
    if status == "running":
        _SECTION_STARTS.setdefault(timer_key, perf_counter())
    elapsed_seconds = None
    if status in {"completed", "failed", "skipped"}:
        started = _SECTION_STARTS.pop(timer_key, None)
        if started is not None:
            elapsed_seconds = round(perf_counter() - started, 2)
            logger.info("Analysis %s: %s %s in %.2fs", analysis_id, section_name, status, elapsed_seconds)

    snapshot.sections[
        section_name
    ] = AnalysisSectionState(
        status=status,
        result=result,
        error=error,
        elapsed_seconds=elapsed_seconds,
    )

    _refresh_finished_sections(
        snapshot
    )


def _skip_section(
    analysis_id: str,
    section_name: str,
    reason: str,
) -> None:
    _set_section(
        analysis_id,
        section_name,
        status="skipped",
        error=reason,
    )


def _fail_section(
    analysis_id: str,
    section_name: str,
    error: Exception | str,
) -> None:
    _set_section(
        analysis_id,
        section_name,
        status="failed",
        error=str(error),
    )


async def run_analysis(analysis_id: str, file_bytes: bytes, filename: str, jd_text: str) -> None:
    snapshot = _ANALYSES[analysis_id]
    snapshot.status = "processing"
    diagnostics = None
    diagnostic_error = None
    try:
        resume_text = await asyncio.to_thread(extract_text, file_bytes, filename)
        if not resume_text.strip() or not jd_text.strip():
            raise ValueError("Resume and job description must contain readable text.")
        if filename.lower().endswith(".pdf"):
            try:
                diagnostics = await asyncio.to_thread(inspect_resume_diagnostics, file_bytes, filename)
            except Exception as error:
                diagnostic_error = str(error)
        for name in SECTION_NAMES:
            if name == "document_health" and diagnostics is None:
                if diagnostic_error:
                    _fail_section(analysis_id, name, diagnostic_error)
                else:
                    _skip_section(analysis_id, name, "Technical document diagnostics support PDF files only.")
            else:
                _set_section(analysis_id, name, status="running")

        result = await asyncio.to_thread(generate_unified_analysis, resume_text, jd_text, diagnostics)
        sections = assemble_sections(result, diagnostics)
        for name in SECTION_NAMES:
            if name in sections:
                _set_section(analysis_id, name, status="completed", result=sections[name])
            elif snapshot.sections[name].status == "running":
                _skip_section(analysis_id, name, "No applicable requirements in the job description.")
        snapshot.status = "completed_with_errors" if diagnostic_error else "completed"
    except Exception as error:
        logger.warning("Analysis %s failed: %s", analysis_id, analysis_error_context(error))
        for name in SECTION_NAMES:
            if snapshot.sections[name].status in {"pending", "running"}:
                _fail_section(analysis_id, name, analysis_error_message(error))
        snapshot.status = "failed"
