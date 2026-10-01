from core.schemas import (
    EvidenceStatus,
    ExperienceFitDiagnostics,
    ExperienceFitRequirement,
    RequirementCategory,
    RequirementImportance,
    RequirementImportanceItem,
    RequirementEvaluation,
)


# --------------- COVERAGE ---------------

def _coverage_score(
    requirements: list[ExperienceFitRequirement],
) -> int | None:
    if not requirements:
        return None

    points = 0.0

    for requirement in requirements:
        if requirement.status == EvidenceStatus.SUPPORTED:
            points += 1.0

        elif requirement.status == EvidenceStatus.PARTIAL:
            points += 0.5

    return round(
        points
        / len(requirements)
        * 100
    )


# --------------- DIAGNOSTICS ---------------

def build_experience_fit_diagnostics(
    evidence_requirements: list[RequirementEvaluation],
    requirement_profile: list[RequirementImportanceItem],
) -> ExperienceFitDiagnostics:
    evidence_map = {
        item.requirement: item
        for item in evidence_requirements
    }

    profile_map = {
        item.requirement: item
        for item in requirement_profile
    }

    if set(evidence_map) != set(profile_map):
        raise ValueError(
            "Evidence requirements and requirement profile "
            "must contain the same requirement set."
        )

    requirements = []

    for requirement_name, profile in profile_map.items():
        if profile.category not in {
            RequirementCategory.EXPERIENCE,
            RequirementCategory.RESPONSIBILITY,
        }:
            continue

        evidence = evidence_map[
            requirement_name
        ]

        requirements.append(
            ExperienceFitRequirement(
                requirement=requirement_name,
                category=profile.category,
                importance=profile.importance,
                status=evidence.status,
                evidence=evidence.evidence,
                jd_signal=profile.jd_signal,
            )
        )

    if not requirements:
        raise ValueError(
            "No experience or responsibility requirements "
            "were identified."
        )

    groups = {
        RequirementImportance.MANDATORY: [],
        RequirementImportance.HIGH_PRIORITY: [],
        RequirementImportance.PREFERRED: [],
        RequirementImportance.OPTIONAL: [],
    }

    experience_group = []
    responsibility_group = []

    supported = 0
    partial = 0
    not_evidenced = 0

    requirements_with_evidence = 0

    missing_mandatory = []
    missing_high_priority = []

    partial_mandatory = []
    partial_high_priority = []

    for requirement in requirements:
        groups[
            requirement.importance
        ].append(
            requirement
        )

        if (
            requirement.category
            == RequirementCategory.EXPERIENCE
        ):
            experience_group.append(
                requirement
            )

        elif (
            requirement.category
            == RequirementCategory.RESPONSIBILITY
        ):
            responsibility_group.append(
                requirement
            )

        if requirement.evidence:
            if requirement.evidence.strip():
                requirements_with_evidence += 1

        if requirement.status == EvidenceStatus.SUPPORTED:
            supported += 1

        elif requirement.status == EvidenceStatus.PARTIAL:
            partial += 1

        else:
            not_evidenced += 1

        if (
            requirement.importance
            == RequirementImportance.MANDATORY
        ):
            if requirement.status == EvidenceStatus.NOT_EVIDENCED:
                missing_mandatory.append(
                    requirement.requirement
                )

            elif requirement.status == EvidenceStatus.PARTIAL:
                partial_mandatory.append(
                    requirement.requirement
                )

        if (
            requirement.importance
            == RequirementImportance.HIGH_PRIORITY
        ):
            if requirement.status == EvidenceStatus.NOT_EVIDENCED:
                missing_high_priority.append(
                    requirement.requirement
                )

            elif requirement.status == EvidenceStatus.PARTIAL:
                partial_high_priority.append(
                    requirement.requirement
                )

    evidence_coverage_score = round(
        requirements_with_evidence
        / len(requirements)
        * 100
    )

    return ExperienceFitDiagnostics(
        total_requirements=len(
            requirements
        ),

        experience_requirements=len(
            experience_group
        ),

        responsibility_requirements=len(
            responsibility_group
        ),

        supported=supported,
        partial=partial,
        not_evidenced=not_evidenced,

        mandatory_count=len(
            groups[
                RequirementImportance.MANDATORY
            ]
        ),

        high_priority_count=len(
            groups[
                RequirementImportance.HIGH_PRIORITY
            ]
        ),

        preferred_count=len(
            groups[
                RequirementImportance.PREFERRED
            ]
        ),

        optional_count=len(
            groups[
                RequirementImportance.OPTIONAL
            ]
        ),

        mandatory_coverage_score=_coverage_score(
            groups[
                RequirementImportance.MANDATORY
            ]
        ),

        high_priority_coverage_score=_coverage_score(
            groups[
                RequirementImportance.HIGH_PRIORITY
            ]
        ),

        responsibility_coverage_score=_coverage_score(
            responsibility_group
        ),

        experience_coverage_score=_coverage_score(
            experience_group
        ),

        evidence_coverage_score=(
            evidence_coverage_score
        ),

        missing_mandatory=missing_mandatory,
        missing_high_priority=missing_high_priority,

        partial_mandatory=partial_mandatory,
        partial_high_priority=partial_high_priority,

        requirements=requirements,
    )
