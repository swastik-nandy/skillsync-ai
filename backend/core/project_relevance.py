from core.project_diagnostics import (
    build_project_diagnostics,
)
from core.project_extractor import (
    extract_projects,
)
from core.project_relevance_evaluator import (
    evaluate_project_relevance,
)
from core.schemas import (
    ProjectRelevanceReport,
    ProjectRelevanceRequest,
)


# --------------- PROJECT RELEVANCE ---------------

def build_project_relevance_report(
    request: ProjectRelevanceRequest,
) -> ProjectRelevanceReport:
    extraction = extract_projects(
        request.resume_text
    )

    diagnostics = build_project_diagnostics(
        extraction.projects
    )

    assessment = evaluate_project_relevance(
        extraction.projects,
        diagnostics,
        request.requirement_profile,
    )

    return ProjectRelevanceReport(
        projects=extraction.projects,
        diagnostics=diagnostics,
        assessment=assessment,
    )
