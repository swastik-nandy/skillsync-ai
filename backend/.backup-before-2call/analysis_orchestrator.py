import asyncio
from uuid import uuid4

from core.analysis_schemas import (
    AnalysisSectionState,
    AnalysisSnapshot,
)
from core.document_health_evaluator import (
    evaluate_document_health,
)
from core.evidence_quality import (
    build_evidence_diagnostics,
)
from core.evidence_quality_evaluator import (
    evaluate_evidence_quality,
)
from core.experience_fit import (
    build_experience_fit_diagnostics,
)
from core.experience_fit_evaluator import (
    evaluate_experience_fit,
)
from core.extractor import extract_text
from core.overall_role_alignment_evaluator import (
    evaluate_overall_role_alignment,
)
from core.pipeline import process_resume_local
from core.project_diagnostics import (
    build_project_diagnostics,
)
from core.project_extractor import extract_projects
from core.project_relevance_evaluator import (
    evaluate_project_relevance,
)
from core.qualification_alignment import (
    build_qualification_diagnostics,
)
from core.qualification_evaluator import (
    evaluate_qualification_alignment,
)
from core.requirement_importance_evaluator import (
    evaluate_requirement_importance,
)
from core.resume_diagnostics import (
    inspect_resume_diagnostics,
)
from core.schemas import (
    EvidenceQualityAssessment,
    EvidenceQualityReport,
    EvidenceStatus,
    ExperienceFitAssessment,
    ExperienceFitReport,
    FeedbackReport,
    OverallRoleAlignmentContext,
    ProjectRelevanceAssessment,
    ProjectRelevanceReport,
    QualificationAssessment,
    QualificationReport,
    RequirementCategory,
    RequirementImportanceReport,
    RequirementImportanceRequest,
    SkillsAlignmentAssessment,
    SkillsAlignmentReport,
)
from core.skills_alignment import (
    build_skills_alignment_diagnostics,
)
from core.skills_alignment_evaluator import (
    evaluate_skills_alignment,
)


# --------------- STORE ---------------

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


# --------------- SERIALIZATION ---------------

def _dump(value) -> dict:
    if hasattr(
        value,
        "model_dump",
    ):
        return value.model_dump(
            mode="json"
        )

    if isinstance(
        value,
        dict,
    ):
        return value

    raise TypeError(
        "Analysis section result must be a Pydantic model or dict."
    )


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

    snapshot.sections[
        section_name
    ] = AnalysisSectionState(
        status=status,
        result=result,
        error=error,
    )

    _refresh_finished_sections(
        snapshot
    )


def _update_section_result(
    analysis_id: str,
    section_name: str,
    result: dict,
) -> None:
    snapshot = _ANALYSES[
        analysis_id
    ]

    snapshot.sections[
        section_name
    ].result = result


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
        error=str(
            error
        ),
    )


# --------------- DOCUMENT HEALTH ---------------

async def _run_document_health(
    analysis_id: str,
    file_bytes: bytes,
    filename: str,
) -> None:
    if not filename.lower().endswith(
        ".pdf"
    ):
        _skip_section(
            analysis_id,
            "document_health",
            "Technical document diagnostics currently support PDF files only.",
        )
        return

    _set_section(
        analysis_id,
        "document_health",
        status="running",
    )

    try:
        diagnostics = await asyncio.to_thread(
            inspect_resume_diagnostics,
            file_bytes,
            filename,
        )

        _update_section_result(
            analysis_id,
            "document_health",
            {
                "diagnostics": _dump(
                    diagnostics
                ),
                "assessment": None,
            },
        )

        assessment = await asyncio.to_thread(
            evaluate_document_health,
            diagnostics,
        )

        _set_section(
            analysis_id,
            "document_health",
            status="completed",
            result={
                "diagnostics": _dump(
                    diagnostics
                ),
                "assessment": _dump(
                    assessment
                ),
            },
        )

    except Exception as error:
        snapshot = _ANALYSES[
            analysis_id
        ]

        existing = snapshot.sections[
            "document_health"
        ].result

        _set_section(
            analysis_id,
            "document_health",
            status="failed",
            result=existing,
            error=str(
                error
            ),
        )


# --------------- FEEDBACK ---------------

async def _run_feedback(
    analysis_id: str,
    resume_text: str,
    jd_text: str,
) -> FeedbackReport | None:
    _set_section(
        analysis_id,
        "feedback",
        status="running",
    )

    try:
        report = await asyncio.to_thread(
            process_resume_local,
            resume_text,
            jd_text,
        )

        strengths = [
            requirement.requirement
            for requirement in report.requirements
            if requirement.status
            == EvidenceStatus.SUPPORTED
        ]

        weaknesses = [
            requirement.requirement
            for requirement in report.requirements
            if requirement.status
            in {
                EvidenceStatus.PARTIAL,
                EvidenceStatus.NOT_EVIDENCED,
            }
        ]

        _set_section(
            analysis_id,
            "feedback",
            status="completed",
            result={
                "match_percentage": report.match_percentage,
                "strengths": strengths,
                "weaknesses": weaknesses,
                "suggestions": report.suggestions,
                "requirements": [
                    requirement.model_dump(
                        mode="json"
                    )
                    for requirement in report.requirements
                ],
            },
        )

        return report

    except Exception as error:
        _fail_section(
            analysis_id,
            "feedback",
            error,
        )

        return None


# --------------- EVIDENCE QUALITY ---------------

async def _run_evidence_quality(
    analysis_id: str,
    report: FeedbackReport,
) -> EvidenceQualityReport | None:
    _set_section(
        analysis_id,
        "evidence_quality",
        status="running",
    )

    try:
        diagnostics = build_evidence_diagnostics(
            report.requirements
        )

        _update_section_result(
            analysis_id,
            "evidence_quality",
            {
                "diagnostics": _dump(
                    diagnostics
                ),
                "assessment": None,
            },
        )

        assessment = await asyncio.to_thread(
            evaluate_evidence_quality,
            diagnostics,
        )

        result = EvidenceQualityReport(
            diagnostics=diagnostics,
            assessment=assessment,
        )

        _set_section(
            analysis_id,
            "evidence_quality",
            status="completed",
            result=_dump(
                result
            ),
        )

        return result

    except Exception as error:
        snapshot = _ANALYSES[
            analysis_id
        ]

        existing = snapshot.sections[
            "evidence_quality"
        ].result

        _set_section(
            analysis_id,
            "evidence_quality",
            status="failed",
            result=existing,
            error=str(
                error
            ),
        )

        return None


# --------------- REQUIREMENT IMPORTANCE ---------------

async def _run_requirement_importance(
    analysis_id: str,
    report: FeedbackReport,
    jd_text: str,
) -> RequirementImportanceReport | None:
    _set_section(
        analysis_id,
        "requirement_importance",
        status="running",
    )

    try:
        request = RequirementImportanceRequest(
            jd_text=jd_text,
            requirements=[
                requirement.requirement
                for requirement in report.requirements
            ],
        )

        result = await asyncio.to_thread(
            evaluate_requirement_importance,
            request,
        )

        _set_section(
            analysis_id,
            "requirement_importance",
            status="completed",
            result=_dump(
                result
            ),
        )

        return result

    except Exception as error:
        _fail_section(
            analysis_id,
            "requirement_importance",
            error,
        )

        return None


# --------------- SKILLS ALIGNMENT ---------------

async def _run_skills_alignment(
    analysis_id: str,
    report: FeedbackReport,
    profile: RequirementImportanceReport,
) -> None:
    has_skills = any(
        item.category
        == RequirementCategory.SKILL
        for item in profile.requirements
    )

    if not has_skills:
        _skip_section(
            analysis_id,
            "skills_alignment",
            "The job description contains no classified skill requirements.",
        )
        return

    _set_section(
        analysis_id,
        "skills_alignment",
        status="running",
    )

    try:
        diagnostics = build_skills_alignment_diagnostics(
            report.requirements,
            profile.requirements,
        )

        _update_section_result(
            analysis_id,
            "skills_alignment",
            {
                "diagnostics": _dump(
                    diagnostics
                ),
                "assessment": None,
            },
        )

        assessment = await asyncio.to_thread(
            evaluate_skills_alignment,
            diagnostics,
        )

        result = SkillsAlignmentReport(
            diagnostics=diagnostics,
            assessment=assessment,
        )

        _set_section(
            analysis_id,
            "skills_alignment",
            status="completed",
            result=_dump(
                result
            ),
        )

    except Exception as error:
        snapshot = _ANALYSES[
            analysis_id
        ]

        existing = snapshot.sections[
            "skills_alignment"
        ].result

        _set_section(
            analysis_id,
            "skills_alignment",
            status="failed",
            result=existing,
            error=str(
                error
            ),
        )


# --------------- EXPERIENCE FIT ---------------

async def _run_experience_fit(
    analysis_id: str,
    report: FeedbackReport,
    profile: RequirementImportanceReport,
) -> None:
    has_experience = any(
        item.category
        in {
            RequirementCategory.EXPERIENCE,
            RequirementCategory.RESPONSIBILITY,
        }
        for item in profile.requirements
    )

    if not has_experience:
        _skip_section(
            analysis_id,
            "experience_fit",
            "The job description contains no classified experience or responsibility requirements.",
        )
        return

    _set_section(
        analysis_id,
        "experience_fit",
        status="running",
    )

    try:
        diagnostics = build_experience_fit_diagnostics(
            report.requirements,
            profile.requirements,
        )

        _update_section_result(
            analysis_id,
            "experience_fit",
            {
                "diagnostics": _dump(
                    diagnostics
                ),
                "assessment": None,
            },
        )

        assessment = await asyncio.to_thread(
            evaluate_experience_fit,
            diagnostics,
        )

        result = ExperienceFitReport(
            diagnostics=diagnostics,
            assessment=assessment,
        )

        _set_section(
            analysis_id,
            "experience_fit",
            status="completed",
            result=_dump(
                result
            ),
        )

    except Exception as error:
        snapshot = _ANALYSES[
            analysis_id
        ]

        existing = snapshot.sections[
            "experience_fit"
        ].result

        _set_section(
            analysis_id,
            "experience_fit",
            status="failed",
            result=existing,
            error=str(
                error
            ),
        )


# --------------- QUALIFICATION ALIGNMENT ---------------

async def _run_qualification_alignment(
    analysis_id: str,
    report: FeedbackReport,
    profile: RequirementImportanceReport,
) -> None:
    _set_section(
        analysis_id,
        "qualification_alignment",
        status="running",
    )

    try:
        diagnostics = build_qualification_diagnostics(
            report.requirements,
            profile.requirements,
        )

        if not diagnostics.applicable:
            result = QualificationReport(
                applicable=False,
                diagnostics=diagnostics,
                assessment=None,
            )

            _set_section(
                analysis_id,
                "qualification_alignment",
                status="completed",
                result=_dump(
                    result
                ),
            )

            return

        _update_section_result(
            analysis_id,
            "qualification_alignment",
            {
                "applicable": True,
                "diagnostics": _dump(
                    diagnostics
                ),
                "assessment": None,
            },
        )

        assessment = await asyncio.to_thread(
            evaluate_qualification_alignment,
            diagnostics,
        )

        result = QualificationReport(
            applicable=True,
            diagnostics=diagnostics,
            assessment=assessment,
        )

        _set_section(
            analysis_id,
            "qualification_alignment",
            status="completed",
            result=_dump(
                result
            ),
        )

    except Exception as error:
        snapshot = _ANALYSES[
            analysis_id
        ]

        existing = snapshot.sections[
            "qualification_alignment"
        ].result

        _set_section(
            analysis_id,
            "qualification_alignment",
            status="failed",
            result=existing,
            error=str(
                error
            ),
        )


# --------------- PROJECT RELEVANCE ---------------

async def _run_project_relevance(
    analysis_id: str,
    resume_text: str,
    profile: RequirementImportanceReport,
) -> None:
    _set_section(
        analysis_id,
        "project_relevance",
        status="running",
    )

    try:
        extraction = await asyncio.to_thread(
            extract_projects,
            resume_text,
        )

        diagnostics = build_project_diagnostics(
            extraction.projects
        )

        _update_section_result(
            analysis_id,
            "project_relevance",
            {
                "projects": [
                    project.model_dump(
                        mode="json"
                    )
                    for project in extraction.projects
                ],
                "diagnostics": _dump(
                    diagnostics
                ),
                "assessment": None,
            },
        )

        assessment = await asyncio.to_thread(
            evaluate_project_relevance,
            extraction.projects,
            diagnostics,
            profile.requirements,
        )

        result = ProjectRelevanceReport(
            projects=extraction.projects,
            diagnostics=diagnostics,
            assessment=assessment,
        )

        _set_section(
            analysis_id,
            "project_relevance",
            status="completed",
            result=_dump(
                result
            ),
        )

    except Exception as error:
        snapshot = _ANALYSES[
            analysis_id
        ]

        existing = snapshot.sections[
            "project_relevance"
        ].result

        _set_section(
            analysis_id,
            "project_relevance",
            status="failed",
            result=existing,
            error=str(
                error
            ),
        )


# --------------- OVERALL ROLE ALIGNMENT ---------------

async def _run_overall_role_alignment(
    analysis_id: str,
    report: FeedbackReport,
    profile: RequirementImportanceReport,
) -> None:
    _set_section(
        analysis_id,
        "overall_role_alignment",
        status="running",
    )

    try:
        snapshot = _ANALYSES[
            analysis_id
        ]

        def assessment(
            section_name: str,
            model,
        ):
            section = snapshot.sections[
                section_name
            ]

            if not section.result:
                return None

            raw = section.result.get(
                "assessment"
            )

            if raw is None:
                return None

            return model.model_validate(
                raw
            )

        context = OverallRoleAlignmentContext(
            requirement_profile=profile.requirements,
            evidence_requirements=report.requirements,
            evidence_quality=assessment(
                "evidence_quality",
                EvidenceQualityAssessment,
            ),
            skills_alignment=assessment(
                "skills_alignment",
                SkillsAlignmentAssessment,
            ),
            experience_fit=assessment(
                "experience_fit",
                ExperienceFitAssessment,
            ),
            qualification_alignment=assessment(
                "qualification_alignment",
                QualificationAssessment,
            ),
            projects_relevance=assessment(
                "project_relevance",
                ProjectRelevanceAssessment,
            ),
        )

        result = await asyncio.to_thread(
            evaluate_overall_role_alignment,
            context,
        )

        _set_section(
            analysis_id,
            "overall_role_alignment",
            status="completed",
            result=_dump(
                result
            ),
        )

    except Exception as error:
        _fail_section(
            analysis_id,
            "overall_role_alignment",
            error,
        )


# --------------- ORCHESTRATION ---------------

async def run_analysis(
    analysis_id: str,
    file_bytes: bytes,
    filename: str,
    jd_text: str,
) -> None:
    snapshot = _ANALYSES[
        analysis_id
    ]

    snapshot.status = "processing"

    document_task = asyncio.create_task(
        _run_document_health(
            analysis_id,
            file_bytes,
            filename,
        )
    )

    try:
        resume_text = await asyncio.to_thread(
            extract_text,
            file_bytes,
            filename,
        )

    except Exception as error:
        _fail_section(
            analysis_id,
            "feedback",
            error,
        )

        for section_name in (
            "evidence_quality",
            "requirement_importance",
            "skills_alignment",
            "experience_fit",
            "qualification_alignment",
            "project_relevance",
            "overall_role_alignment",
        ):
            _skip_section(
                analysis_id,
                section_name,
                "Resume text extraction failed.",
            )

        await document_task

        snapshot.status = "failed"
        return

    report = await _run_feedback(
        analysis_id,
        resume_text,
        jd_text,
    )

    if report is None:
        for section_name in (
            "evidence_quality",
            "requirement_importance",
            "skills_alignment",
            "experience_fit",
            "qualification_alignment",
            "project_relevance",
            "overall_role_alignment",
        ):
            _skip_section(
                analysis_id,
                section_name,
                "Requirement evidence generation failed.",
            )

        await document_task

        snapshot.status = "failed"
        return

    evidence_task = asyncio.create_task(
        _run_evidence_quality(
            analysis_id,
            report,
        )
    )

    importance__________________________________________tion as error:
          "overall_role_aligror:
          "overa xt,
            jd_port,
     _,dbackRep     resume_text gathe        err    return

          j   )
    )

   
        jd_textbackRep 

    if report is None:
        for section_name in",
            "skills_alignment",
            "experience_fit",
            "qualification_alignment",
            "project_relevance",
            "overall_role_alignment",
        ):
            _skip_section(
                analysis_id,
                                              )
    )tion contct evidence generation failed.",
   elsif report i  resume_text gathe        err     ---

async def _run_skillsip_section(
                analysis_id,
r:
          "overa     backRepcationAssessment,
           ----

async def _run_expeip_section(
                analysis_id,
r:
          "overa     backRepcationAssessment,
           ----

async def _run_qualificationip_section(
                analysis_id,
r:
          "overa     backRepcationAssessment,
           ----

async def _run_projectip_section(
                analysis_id,
r:,
            resume_te    backRepcationAssessment,
       .",
            )----

async def _run_overall_roleection(
                analysis_r:
          "overa backRepcationAsse.",
        )

        await docence gnapshot.fininapshot.sections[ report is None:
        for section in snapshot.sectiooooos_id= sum(
       =snapshot.status]  jd_textence gnapshot.f,
    )

    try:
        sna        s_ame._k",
 s",
   elsif report i   try:
        sna        s"
                