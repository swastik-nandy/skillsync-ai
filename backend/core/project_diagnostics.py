from core.schemas import (
    ProjectDiagnostic,
    ProjectRelevanceDiagnostics,
    ResumeProject,
)


# --------------- PERCENTAGE ---------------

def _percentage(
    value: int,
    total: int,
) -> int:
    if total == 0:
        return 0

    return round(
        value / total * 100
    )


# --------------- PROJECT COMPLETENESS ---------------

def _project_completeness(
    project: ResumeProject,
) -> int:
    signals = [
        bool(
            project.description.strip()
        ),
        bool(
            project.technologies
        ),
        bool(
            project.responsibilities
        ),
        bool(
            project.outcomes
        ),
        bool(
            project.evidence
        ),
    ]

    return round(
        sum(signals)
        / len(signals)
        * 100
    )


# --------------- DIAGNOSTICS ---------------

def build_project_diagnostics(
    projects: list[ResumeProject],
) -> ProjectRelevanceDiagnostics:
    total = len(
        projects
    )

    projects_with_technologies = 0
    projects_with_outcomes = 0
    projects_with_metrics = 0
    projects_with_production = 0

    project_diagnostics = []

    completeness_scores = []

    for project in projects:
        if project.technologies:
            projects_with_technologies += 1

        if project.outcomes:
            projects_with_outcomes += 1

        if project.quantified_metrics:
            projects_with_metrics += 1

        if project.production_signals:
            projects_with_production += 1

        completeness = (
            _project_completeness(
                project
            )
        )

        completeness_scores.append(
            completeness
        )

        project_diagnostics.append(
            ProjectDiagnostic(
                name=project.name,

                technology_count=len(
                    project.technologies
                ),

                responsibility_count=len(
                    project.responsibilities
                ),

                outcome_count=len(
                    project.outcomes
                ),

                quantified_metric_count=len(
                    project.quantified_metrics
                ),

                production_signal_count=len(
                    project.production_signals
                ),

                evidence_completeness_score=(
                    completeness
                ),
            )
        )

    project_evidence_score = (
        round(
            sum(
                completeness_scores
            )
            / len(
                completeness_scores
            )
        )
        if completeness_scores
        else 0
    )

    return ProjectRelevanceDiagnostics(
        total_projects=total,

        projects_with_technologies=(
            projects_with_technologies
        ),

        projects_with_outcomes=(
            projects_with_outcomes
        ),

        projects_with_quantified_metrics=(
            projects_with_metrics
        ),

        projects_with_production_signals=(
            projects_with_production
        ),

        technology_evidence_score=_percentage(
            projects_with_technologies,
            total,
        ),

        outcome_evidence_score=_percentage(
            projects_with_outcomes,
            total,
        ),

        quantified_impact_score=_percentage(
            projects_with_metrics,
            total,
        ),

        production_depth_score=_percentage(
            projects_with_production,
            total,
        ),

        project_evidence_score=(
            project_evidence_score
        ),

        projects=project_diagnostics,
    )
