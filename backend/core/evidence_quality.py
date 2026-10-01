from core.schemas import (
    EvidenceDiagnostics,
    EvidenceRequirementDiagnostic,
    EvidenceStatus,
    RequirementEvaluation,
)


# --------------- HELPERS ---------------

def _percentage(
    value: int,
    total: int,
) -> float:
    if total == 0:
        return 0.0

    return round(
        value / total * 100,
        1,
    )


# --------------- DIAGNOSTICS ---------------

def build_evidence_diagnostics(
    requirements: list[RequirementEvaluation],
) -> EvidenceDiagnostics:
    total = len(
        requirements
    )

    supported = 0
    partial = 0
    not_evidenced = 0

    requirements_with_evidence = 0
    mismatches = 0

    diagnostics = []

    for requirement in requirements:
        evidence = (
            requirement.evidence.strip()
            if requirement.evidence
            else None
        )

        has_evidence = bool(
            evidence
        )

        if has_evidence:
            requirements_with_evidence += 1

        if (
            requirement.status
            == EvidenceStatus.SUPPORTED
        ):
            supported += 1

            if not has_evidence:
                mismatches += 1

        elif (
            requirement.status
            == EvidenceStatus.PARTIAL
        ):
            partial += 1

            if not has_evidence:
                mismatches += 1

        else:
            not_evidenced += 1

            if has_evidence:
                mismatches += 1

        diagnostics.append(
            EvidenceRequirementDiagnostic(
                requirement=requirement.requirement,
                status=requirement.status,
                evidence=evidence,
                has_evidence=has_evidence,
                evidence_characters=(
                    len(evidence)
                    if evidence
                    else 0
                ),
            )
        )

    supported_percentage = (
        _percentage(
            supported,
            total,
        )
    )

    partial_percentage = (
        _percentage(
            partial,
            total,
        )
    )

    not_evidenced_percentage = (
        _percentage(
            not_evidenced,
            total,
        )
    )

    evidence_coverage_percentage = (
        _percentage(
            requirements_with_evidence,
            total,
        )
    )

    # --------------- DEBUG INDEX ---------------

    weighted_support = (
        supported
        + partial * 0.5
    )

    deterministic_index = (
        round(
            weighted_support
            / total
            * 100
        )
        if total
        else 0
    )

    if mismatches:
        deterministic_index = max(
            0,
            deterministic_index
            - min(
                mismatches * 5,
                20,
            ),
        )

    return EvidenceDiagnostics(
        total_requirements=total,

        supported=supported,
        partial=partial,
        not_evidenced=not_evidenced,

        supported_percentage=supported_percentage,
        partial_percentage=partial_percentage,
        not_evidenced_percentage=not_evidenced_percentage,

        requirements_with_evidence=requirements_with_evidence,

        evidence_coverage_percentage=(
            evidence_coverage_percentage
        ),

        status_evidence_mismatches=mismatches,

        deterministic_evidence_index=(
            deterministic_index
        ),

        requirements=diagnostics,
    )
