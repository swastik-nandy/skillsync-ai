from core.schemas import (
    EvidenceStatus,
    RequirementCategory,
    RequirementImportance,
    RequirementImportanceItem,
    RequirementEvaluation,
    SkillAlignmentDiagnostics,
    SkillAlignmentRequirement,
)


# --------------- COVERAGE ---------------

def _coverage_score(
    requirements: list[SkillAlignmentRequirement],
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

def build_skills_alignment_diagnostics(
    evidence_requirements: list[RequirementEvaluation],
    requirement_profile: list[RequirementImportanceItem],
) -> SkillAlignmentDiagnostics:
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

    skill_requirements = []

    for requirement_name, profile in profile_map.items():
        if profile.category != RequirementCategory.SKILL:
            continue

        evidence = evidence_map[
            requirement_name
        ]

        skill_requirements.append(
            SkillAlignmentRequirement(
                requirement=requirement_name,
                importance=profile.importance,
                status=evidence.status,
                evidence=evidence.evidence,
                jd_signal=profile.jd_signal,
            )
        )

    if not skill_requirements:
        raise ValueError(
            "No skill requirements were identified."
        )

    groups = {
        RequirementImportance.MANDATORY: [],
        RequirementImportance.HIGH_PRIORITY: [],
        RequirementImportance.PREFERRED: [],
        RequirementImportance.OPTIONAL: [],
    }

    supported = 0
    partial = 0
    not_evidenced = 0

    missing_mandatory = []
    missing_high_priority = []

    partial_mandatory = []
    partial_high_priority = []

    evidence_points = 0.0

    for requirement in skill_requirements:
        groups[
            requirement.importance
        ].append(
            requirement
        )

        if requirement.status == EvidenceStatus.SUPPORTED:
            supported += 1
            evidence_points += 1.0

        elif requirement.status == EvidenceStatus.PARTIAL:
            partial += 1
            evidence_points += 0.5

        else:
            not_evidenced += 1

        if (
            requirement.importance
            == RequirementImportance.MANDATORY
        ):
            if (
                requirement.status
                == EvidenceStatus.NOT_EVIDENCED
            ):
                missing_mandatory.append(
                    requirement.requirement
                )

            elif (
                requirement.status
                == EvidenceStatus.PARTIAL
            ):
                partial_mandatory.append(
                    requirement.requirement
                )

        if (
            requirement.importance
            == RequirementImportance.HIGH_PRIORITY
        ):
            if (
                requirement.status
                == EvidenceStatus.NOT_EVIDENCED
            ):
                missing_high_priority.append(
                    requirement.requirement
                )

            elif (
                requirement.status
                == EvidenceStatus.PARTIAL
            ):
                partial_high_priority.append(
                    requirement.requirement
                )

    evidence_strength_score = round(
        evidence_points
        / len(skill_requirements)
        * 100
    )

    return SkillAlignmentDiagnostics(
        total_skill_requirements=len(
            skill_requirements
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

        preferred_coverage_score=_coverage_score(
            groups[
                RequirementImportance.PREFERRED
            ]
        ),

        optional_coverage_score=_coverage_score(
            groups[
                RequirementImportance.OPTIONAL
            ]
        ),

        evidence_strength_score=(
            evidence_strength_score
        ),

        missing_mandatory=missing_mandatory,
        missing_high_priority=missing_high_priority,

        partial_mandatory=partial_mandatory,
        partial_high_priority=partial_high_priority,

        requirements=skill_requirements,
    )
