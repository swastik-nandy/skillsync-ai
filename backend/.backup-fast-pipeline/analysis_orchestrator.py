import asyncio
import logging
import time
from uuid import uuid4

from core.analysis_schemas import (
    AnalysisSectionState,
    AnalysisSnapshot,
)
from core.extractor import extract_text
from core.fast_analysis import (
    assemble_sections,
    build_local_context,
    generate_foundation,
    generate_scores,
)
from core.resume_diagnostics import (
    inspect_resume_diagnostics,
)


# --------------- SECTIONS ---------------

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

logger = logging.getLogger("uvicorn.error")


_ANALYSES: dict[
    str,
    AnalysisSnapshot,
] = {}


# --------------- STATE ---------------

def create_analysis(
    filename: str,
) -> AnalysisSnapshot:
    analysis_id = str(
        uuid4()
    )

    snapshot = (
        AnalysisSnapshot(
            analysis_id=
                analysis_id,

            status=
                "queued",

            filename=
                filename,

            finished_sections=
                0,

            total_sections=
                len(
                    SECTION_NAMES
                ),

            sections={
                name:
                    AnalysisSectionState()
                for name
                in SECTION_NAMES
            },
        )
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


def _refresh_finished(
    snapshot:
        AnalysisSnapshot,
) -> None:
    terminal = {
        "completed",
        "failed",
        "skipped",
    }

    snapshot.finished_sections = sum(
        section.status
        in terminal
        for section
        in snapshot.sections.values()
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

    snapshot.sections[
        section_name
    ] = (
        AnalysisSectionState(
            status=
                status,

            result=
                result,

            error=
                error,
        )
    )

    _refresh_finished(
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


# --------------- ANALYSIS ---------------

async def run_analysis(
    analysis_id: str,
    file_bytes: bytes,
    filename: str,
    jd_text: str,
) -> None:
    snapshot = _ANALYSES[
        analysis_id
    ]

    snapshot.status = (
        "processing"
    )

    analysis_started_at = (
        time.perf_counter()
    )

    logger.info(
        "Analysis %s started filename=%s bytes=%s jd_chars=%s",
        analysis_id,
        filename,
        len(file_bytes),
        len(jd_text),
    )

    try:
        extract_task = (
            asyncio.to_thread(
                extract_text,
                file_bytes,
                filename,
            )
        )

        diagnostics_task = None

        if (
            filename
            .lower()
            .endswith(
                ".pdf"
            )
        ):
            diagnostics_task = (
                asyncio.to_thread(
                    inspect_resume_diagnostics,
                    file_bytes,
                    filename,
                )
            )

        if diagnostics_task:
            (
                resume_result,
                diagnostics_result,
            ) = await asyncio.gather(
                extract_task,
                diagnostics_task,
                return_exceptions=True,
            )

            if isinstance(
                resume_result,
                Exception,
            ):
                raise resume_result

            resume_text = (
                resume_result
            )

            if isinstance(
                diagnostics_result,
                Exception,
            ):
                document_diagnostics = None

                document_error = str(
                    diagnostics_result
                )

            else:
                document_diagnostics = (
                    diagnostics_result
                )

                document_error = None

        else:
            resume_text = (
                await extract_task
            )

            document_diagnostics = None
            document_error = None

        if not resume_text.strip():
            raise ValueError(
                "Resume contains no readable text."
            )

        if not jd_text.strip():
            raise ValueError(
                "Job description cannot be empty."
            )

        if document_diagnostics:
            _set_section(
                analysis_id,
                "document_health",
                status="running",
                result={
                    "diagnostics":
                        document_diagnostics
                        .model_dump(
                            mode="json"
                        ),

                    "assessment":
                        None,
                },
            )

        elif document_error:
            _set_section(
                analysis_id,
                "document_health",
                status="failed",
                error=document_error,
            )

        else:
            _skip_section(
                analysis_id,
                "document_health",
                "Technical document diagnostics currently support PDF files only.",
            )

        _set_section(
            analysis_id,
            "feedback",
            status="running",
        )

        _set_section(
            analysis_id,
            "requirement_importance",
            status="running",
        )

        # --------------- GROQ CALL 1 ---------------

        logger.info(
            "Analysis %s entering Groq call 1: foundation",
            analysis_id,
        )

        foundation = (
            await asyncio.to_thread(
                generate_foundation,
                resume_text,
                jd_text,
            )
        )

        logger.info(
            "Analysis %s Groq call 1 complete",
            analysis_id,
        )

        local_context = (
            build_local_context(
                foundation,
                document_diagnostics,
            )
        )

        logger.info(
            "Analysis %s local diagnostics complete",
            analysis_id,
        )

        evidence = (
            local_context[
                "evidence"
            ]
        )

        _set_section(
            analysis_id,
            "feedback",
            status="completed",
            result={
                "match_percentage":
                    None,

                "strengths": [
                    item.requirement
                    for item
                    in evidence
                    if (
                        item.status.value
                        == "SUPPORTED"
                    )
                ],

                "weaknesses": [
                    item.requirement
                    for item
                    in evidence
                    if (
                        item.status.value
                        != "SUPPORTED"
                    )
                ],

                "suggestions":
                    foundation.suggestions,

                "requirements": [
                    item.model_dump(
                        mode="json"
                    )
                    for item
                    in evidence
                ],
            },
        )

        _set_section(
            analysis_id,
            "requirement_importance",
            status="completed",
            result=(
                local_context[
                    "importance"
                ]
                .model_dump(
                    mode="json"
                )
            ),
        )

        _set_section(
            analysis_id,
            "evidence_quality",
            status="running",
            result={
                "diagnostics":
                    local_context[
                        "evidence_diagnostics"
                    ]
                    .model_dump(
                        mode="json"
                    ),

                "assessment":
                    None,
            },
        )

        if local_context[
            "skills_diagnostics"
        ]:
            _set_section(
                analysis_id,
                "skills_alignment",
                status="running",
                result={
                    "diagnostics":
                        local_context[
                            "skills_diagnostics"
                        ]
                        .model_dump(
                            mode="json"
                        ),

                    "assessment":
                        None,
                },
            )

        else:
            _skip_section(
                analysis_id,
                "skills_alignment",
                "No skill requirements were identified.",
            )

        if local_context[
            "experience_diagnostics"
        ]:
            _set_section(
                analysis_id,
                "experience_fit",
                status="running",
                result={
                    "diagnostics":
                        local_context[
                            "experience_diagnostics"
                        ]
                        .model_dump(
                            mode="json"
                        ),

                    "assessment":
                        None,
                },
            )

        else:
            _skip_section(
                analysis_id,
                "experience_fit",
                "No experience or responsibility requirements were identified.",
            )

        qualification = (
            local_context[
                "qualification_diagnostics"
            ]
        )

        if qualification.applicable:
            _set_section(
                analysis_id,
                "qualification_alignment",
                status="running",
                result={
                    "applicable":
                        True,

                    "diagnostics":
                        qualification
                        .model_dump(
                            mode="json"
                        ),

                    "assessment":
                        None,
                },
            )

        else:
            _set_section(
                analysis_id,
                "qualification_alignment",
                status="completed",
                result={
                    "applicable":
                        False,

                    "diagnostics":
                        qualification
                        .model_dump(
                            mode="json"
                        ),

                    "assessment":
                        None,
                },
            )

        _set_section(
            analysis_id,
            "project_relevance",
            status="running",
            result={
                "projects": [
                    item.model_dump(
                        mode="json"
                    )
                    for item
                    in foundation.projects
                ],

                "diagnostics":
                    local_context[
                        "project_diagnostics"
                    ]
                    .model_dump(
                        mode="json"
                    ),

                "assessment":
                    None,
            },
        )

        _set_section(
            analysis_id,
            "overall_role_alignment",
            status="running",
        )

        # --------------- GROQ CALL 2 ---------------

        logger.info(
            "Analysis %s entering Groq call 2: scoring",
            analysis_id,
        )

        scores = (
            await asyncio.to_thread(
                generate_scores,
                foundation,
                local_context,
            )
        )

        sections = (
            assemble_sections(
                foundation,
                local_context,
                scores,
            )
        )

        for (
            section_name,
            result,
        ) in sections.items():
            _set_section(
                analysis_id,
                section_name,
                status="completed",
                result=result,
            )

        snapshot.status = (
            "completed_with_errors"
            if document_error
            else "completed"
        )

        logger.info(
            "Analysis %s completed status=%s total_time=%.2fs",
            analysis_id,
            snapshot.status,
            time.perf_counter()
            - analysis_started_at,
        )

    except Exception as error:
        logger.exception(
            "Analysis %s failed after %.2fs: %s",
            analysis_id,
            time.perf_counter()
            - analysis_started_at,
            error,
        )
        for section_name in (
            SECTION_NAMES
        ):
            if (
                snapshot.sections[
                    section_name
                ].status
                in {
                    "pending",
                    "running",
                }
            ):
                _set_section(
                    analysis_id,
                    section_name,
                    status="failed",
                    error=str(
                        error
                    ),
                )

        snapshot.status = (
            "failed"
        )
