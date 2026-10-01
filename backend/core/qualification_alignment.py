from core.schemas import (
    EvidenceStatus,
    QualificationDiagnostics,
    QualificationRequirement,
    RequirementCategory,
    RequirementImportance,
    RequirementImportanceItem,
    RequirementEvaluation,
)


# --------------- COVERAGE ---------------

def _coverage_score(
    requirements: list[QualificationRequirement],
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

def build_qualification_diagnostics(
    evidence_requirements: list[RequirementEvaluation],
    requirement_profile: list[RequirementImportanceItem],
) -> QualificationDiagnostics:
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
            RequirementCategory.EDUCATION,
            RequirementCategory.CERTIFICATION,
        }:
            continue

        evidence = evidence_map[
            requirement_name
        ]

        requirements.append(
            QualificationRequirement(
                requirement=requirement_name,
                category=profile.category,
                importance=profile.importance,
                status=evidence.status,
                evidence=evidence.evidence,
                jd_signal=profile.jd_signal,
            )
        )

    if not requirements:
        return QualificationDiagnostics(
            applicable=False,

            total_requirements=0,
            education_requirements=0,
            certification_requirements=0,

            supported=0,
            partial=0,
            not_evidenced=0,

            mandatory_count=0,
            high_priority_count=0,
            preferred_count=0,
            optional_count=0,

            mandatory_coverage_score=None,
            high_priority_coverage_score=None,
            education_coverage_score=None,
            certification_coverage_score=None,

            missing_mandatory=[],
            missing_high_priority=[],
            partial_critical=[],

            requirements=[],
        )

    groups = {
        RequirementImportance.MANDATORY: [],
        RequirementImportance.HIGH_PRIORITY: [],
        RequirementImportance.PREFERRED: [],
        RequirementImportance.OPTIONAL: [],
    }

    education_group = []
    certification_group = []

    supported = 0
    partial = 0
    not_evidenced = 0

    missing_mandatory = []
    missing_high_priority = []
    partial_critical = []

    for requirement in requirements:
        groups[
            requirement.importance
        ].append(
            requirement
        )

        if (
            requirement.category
            == RequirementCategory.EDUCATION
        ):
            education_group.append(
                requirement
            )

        elif (
            requirement.category
            == RequirementCategory.CERTIFICATION
        ):
            certification_group.append(
                requirement
            )

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
                partial_critical.append(
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
                partial_critical.append(
                    requirement.requirement
                )

    return QualificationDiagnostics(
        applicable=True,

        total_requirements=len(
            requirements
        ),

        education_requirements=len(
            education_group
        ),

        certification_requirements=len(
            certification_group
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

        education_coverage_score=_coverage_score(
            education_group
        ),

        certification_coverage_score=_coverage_score(
            certification_group
        ),

        missing_mandatory=missing_mandatory,
        missing_high_priority=missing_high_priority,
        partial_critical=partial_critical,

        requirements=requirements,
    )
