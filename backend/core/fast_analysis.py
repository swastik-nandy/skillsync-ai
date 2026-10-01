import json
import logging
import time
from collections import Counter
from typing import Literal

from pydantic import Field, model_validator

from core.evidence_quality import build_evidence_diagnostics
from core.experience_fit import build_experience_fit_diagnostics
from core.llm import client, config
from core.project_diagnostics import build_project_diagnostics
from core.prompts import load_prompt
from core.qualification_alignment import (
    build_qualification_diagnostics,
)
from core.schemas import (
    EvidenceStatus,
    RequirementCategory,
    RequirementEvaluation,
    RequirementImportance,
    RequirementImportanceItem,
    RequirementImportanceReport,
    ResumeProject,
    StrictModel,
)
from core.skills_alignment import (
    build_skills_alignment_diagnostics,
)


logger = logging.getLogger("uvicorn.error")


# --------------- FOUNDATION ---------------

class FoundationRequirement(
    RequirementEvaluation
):
    importance: RequirementImportance
    category: RequirementCategory
    jd_signal: str = ""
    reason: str = ""


class FoundationResponse(
    StrictModel
):
    requirements: list[
        FoundationRequirement
    ] = Field(
        min_length=1,
    )

    projects: list[
        ResumeProject
    ]

    suggestions: list[
        str
    ] = Field(
        default_factory=list,
    )

    @model_validator(
        mode="after"
    )
    def validate_requirements(
        self,
    ):
        names = [
            item.requirement
            .strip()
            .casefold()
            for item
            in self.requirements
        ]

        if (
            not all(
                names
            )
            or len(
                set(
                    names
                )
            )
            != len(
                names
            )
        ):
            raise ValueError(
                "Requirements must be nonempty and unique."
            )

        for item in self.requirements:
            if (
                item.status
                == EvidenceStatus.NOT_EVIDENCED
                and item.evidence
                is not None
            ):
                raise ValueError(
                    "NOT_EVIDENCED requirements must have null evidence."
                )

            if (
                item.status
                != EvidenceStatus.NOT_EVIDENCED
                and not (
                    item.evidence
                    or ""
                ).strip()
            ):
                raise ValueError(
                    "SUPPORTED and PARTIAL requirements need evidence."
                )

        return self


# --------------- SCORING ---------------

class ScoreFactor(
    StrictModel
):
    factor: str

    section: str | None = None

    impact: Literal[
        "positive",
        "negative",
        "neutral",
    ] = "neutral"

    impact_strength: Literal[
        "low",
        "medium",
        "high",
    ] = "medium"

    reason: str


class ScoreAssessment(
    StrictModel
):
    score: int = Field(
        ge=0,
        le=100,
    )

    rating: Literal[
        "excellent",
        "strong",
        "good",
        "fair",
        "weak",
    ]

    risk: Literal[
        "low",
        "moderate",
        "high",
        "severe",
    ]

    summary: str

    factors: list[
        ScoreFactor
    ] = Field(
        default_factory=list,
    )

    strengths: list[
        str
    ] = Field(
        default_factory=list,
    )

    partial: list[
        str
    ] = Field(
        default_factory=list,
    )

    gaps: list[
        str
    ] = Field(
        default_factory=list,
    )

    improvements: list[
        str
    ] = Field(
        default_factory=list,
    )


class ScoringResponse(
    StrictModel
):
    document_health: (
        ScoreAssessment
        | None
    ) = None

    evidence_quality: (
        ScoreAssessment
        | None
    ) = None

    skills_alignment: (
        ScoreAssessment
        | None
    ) = None

    experience_fit: (
        ScoreAssessment
        | None
    ) = None

    qualification_alignment: (
        ScoreAssessment
        | None
    ) = None

    project_relevance: (
        ScoreAssessment
        | None
    ) = None

    overall_role_alignment: (
        ScoreAssessment
    )


# --------------- RESPONSE MAPPING ---------------

ASSESSMENT_FIELDS = {
    "document_health": (
        "document_health_score",
        "processing_risk",
        {
            "gaps":
                "critical_issues",
        },
    ),

    "evidence_quality": (
        "evidence_quality_score",
        "evidence_risk",
        {
            "partial":
                "weak_evidence_requirements",

            "gaps":
                "unevidenced_requirements",
        },
    ),

    "skills_alignment": (
        "skills_alignment_score",
        "alignment_risk",
        {
            "strengths":
                "core_requirements_satisfied",

            "partial":
                "partial_requirements",

            "gaps":
                "missing_critical_requirements",
        },
    ),

    "experience_fit": (
        "experience_fit_score",
        "experience_risk",
        {
            "strengths":
                "core_experience_satisfied",

            "partial":
                "partial_experience_requirements",

            "gaps":
                "missing_critical_experience",
        },
    ),

    "qualification_alignment": (
        "qualification_score",
        "qualification_risk",
        {
            "strengths":
                "satisfied_qualifications",

            "partial":
                "partial_qualifications",

            "gaps":
                "missing_critical_qualifications",
        },
    ),

    "project_relevance": (
        "projects_relevance_score",
        "project_fit_risk",
        {
            "strengths":
                "strongest_projects",

            "partial":
                "partially_relevant_projects",

            "gaps":
                "missing_project_evidence",
        },
    ),

    "overall_role_alignment": (
        "overall_role_alignment_score",
        "screening_risk",
        {
            "strengths":
                "strongest_alignment_areas",

            "gaps":
                "critical_gaps",

            "improvements":
                "priority_improvements",
        },
    ),
}


# --------------- GROQ ---------------

def _call_groq(
    config_name: str,
    prompt_name: str,
    payload: dict,
) -> str:
    settings = config[
        "llm"
    ][
        config_name
    ]

    prompt = load_prompt(
        prompt_name
    )

    response = (
        client
        .with_options(
            max_retries=0,
            timeout=settings[
                "timeout_seconds"
            ],
        )
        .chat
        .completions
        .create(
            model=settings[
                "model"
            ],

            temperature=settings[
                "temperature"
            ],

            reasoning_effort=settings[
                "reasoning_effort"
            ],

            include_reasoning=False,

            max_completion_tokens=settings[
                "max_completion_tokens"
            ],

            messages=[
                {
                    "role":
                        "system",

                    "content":
                        prompt[
                            "system_prompt"
                        ],
                },

                {
                    "role":
                        "user",

                    "content":
                        json.dumps(
                            payload,
                            ensure_ascii=False,
                        ),
                },
            ],

            response_format={
                "type":
                    "json_object",
            },
        )
    )

    choice = (
        response
        .choices[0]
    )

    usage = getattr(
        response,
        "usage",
        None,
    )

    prompt_tokens = getattr(
        usage,
        "prompt_tokens",
        None,
    )

    completion_tokens = getattr(
        usage,
        "completion_tokens",
        None,
    )

    total_tokens = getattr(
        usage,
        "total_tokens",
        None,
    )

    content = (
        choice
        .message
        .content
    )

    logger.info(
        "Groq response [%s] model=%s finish_reason=%s "
        "prompt_tokens=%s completion_tokens=%s total_tokens=%s "
        "content_chars=%s",
        config_name,
        settings["model"],
        choice.finish_reason,
        prompt_tokens,
        completion_tokens,
        total_tokens,
        len(content or ""),
    )

    if (
        choice.finish_reason
        != "stop"
        or not content
    ):
        logger.error(
            "Incomplete Groq response [%s]: "
            "finish_reason=%s content_present=%s "
            "prompt_tokens=%s completion_tokens=%s total_tokens=%s "
            "max_completion_tokens=%s",
            config_name,
            choice.finish_reason,
            bool(content),
            prompt_tokens,
            completion_tokens,
            total_tokens,
            settings[
                "max_completion_tokens"
            ],
        )

        raise RuntimeError(
            "Groq returned an incomplete response "
            f"for {config_name}: "
            f"finish_reason={choice.finish_reason}, "
            f"completion_tokens={completion_tokens}, "
            f"max_completion_tokens="
            f"{settings['max_completion_tokens']}"
        )

    return content


# --------------- GROQ CALL 1 ---------------

def generate_foundation(
    resume_text: str,
    jd_text: str,
) -> FoundationResponse:
    settings = config[
        "llm"
    ][
        "fast_foundation"
    ]

    if (
        not resume_text.strip()
        or not jd_text.strip()
    ):
        raise ValueError(
            "Resume and job description must contain readable text."
        )

    if (
        len(
            resume_text
        )
        + len(
            jd_text
        )
        > settings[
            "max_input_characters"
        ]
    ):
        raise ValueError(
            "Resume and job description are too long."
        )

    started_at = time.perf_counter()

    logger.info(
        "Starting Groq call [fast_foundation]: "
        "resume_chars=%s jd_chars=%s",
        len(resume_text),
        len(jd_text),
    )

    content = _call_groq(
        "fast_foundation",
        "fast_foundation",
        {
            "resume_text":
                resume_text,

            "job_description":
                jd_text,
        },
    )

    result = (
        FoundationResponse
        .model_validate_json(
            content
        )
    )

    logger.info(
        "Completed Groq call [fast_foundation] "
        "in %.2fs requirements=%s projects=%s suggestions=%s",
        time.perf_counter()
        - started_at,
        len(
            result.requirements
        ),
        len(
            result.projects
        ),
        len(
            result.suggestions
        ),
    )

    return result


# --------------- LOCAL DIAGNOSTICS ---------------

def build_local_context(
    foundation:
        FoundationResponse,

    document_diagnostics=None,
) -> dict:
    evidence = [
        RequirementEvaluation(
            requirement=
                item.requirement,

            status=
                item.status,

            evidence=
                item.evidence,
        )
        for item
        in foundation.requirements
    ]

    profile = [
        RequirementImportanceItem(
            requirement=
                item.requirement,

            importance=
                item.importance,

            category=
                item.category,

            jd_signal=
                item.jd_signal,

            reason=
                item.reason,
        )
        for item
        in foundation.requirements
    ]

    categories = {
        item.category
        for item
        in profile
    }

    counts = Counter(
        item.importance
        .value
        .lower()
        for item
        in profile
    )

    importance = (
        RequirementImportanceReport(
            total_requirements=
                len(
                    profile
                ),

            mandatory=
                counts[
                    "mandatory"
                ],

            high_priority=
                counts[
                    "high_priority"
                ],

            preferred=
                counts[
                    "preferred"
                ],

            optional=
                counts[
                    "optional"
                ],

            requirements=
                profile,
        )
    )

    skills = None

    if (
        RequirementCategory.SKILL
        in categories
    ):
        skills = (
            build_skills_alignment_diagnostics(
                evidence,
                profile,
            )
        )

    experience = None

    if categories & {
        RequirementCategory.EXPERIENCE,
        RequirementCategory.RESPONSIBILITY,
    }:
        experience = (
            build_experience_fit_diagnostics(
                evidence,
                profile,
            )
        )

    return {
        "evidence":
            evidence,

        "profile":
            profile,

        "importance":
            importance,

        "evidence_diagnostics":
            build_evidence_diagnostics(
                evidence
            ),

        "skills_diagnostics":
            skills,

        "experience_diagnostics":
            experience,

        "qualification_diagnostics":
            build_qualification_diagnostics(
                evidence,
                profile,
            ),

        "project_diagnostics":
            build_project_diagnostics(
                foundation.projects
            ),

        "document_diagnostics":
            document_diagnostics,
    }


# --------------- GROQ CALL 2 ---------------

def generate_scores(
    foundation:
        FoundationResponse,

    local_context:
        dict,
) -> ScoringResponse:
    diagnostics = {}

    for (
        source_key,
        output_key,
    ) in (
        (
            "evidence_diagnostics",
            "evidence_quality",
        ),

        (
            "skills_diagnostics",
            "skills_alignment",
        ),

        (
            "experience_diagnostics",
            "experience_fit",
        ),

        (
            "qualification_diagnostics",
            "qualification_alignment",
        ),

        (
            "project_diagnostics",
            "project_relevance",
        ),

        (
            "document_diagnostics",
            "document_health",
        ),
    ):
        value = local_context[
            source_key
        ]

        diagnostics[
            output_key
        ] = (
            value.model_dump(
                mode="json"
            )
            if value
            is not None
            else None
        )

    started_at = time.perf_counter()

    logger.info(
        "Starting Groq call [fast_scoring]: "
        "requirements=%s projects=%s",
        len(
            foundation.requirements
        ),
        len(
            foundation.projects
        ),
    )

    content = _call_groq(
        "fast_scoring",
        "fast_scoring",
        {
            "requirements": [
                {
                    "requirement":
                        item.requirement,

                    "status":
                        item.status.value,

                    "importance":
                        item.importance.value,

                    "category":
                        item.category.value,

                    "evidence":
                        item.evidence,
                }
                for item
                in foundation.requirements
            ],

            "projects": [
                item.model_dump(
                    mode="json"
                )
                for item
                in foundation.projects
            ],

            "diagnostics":
                diagnostics,
        },
    )

    result = (
        ScoringResponse
        .model_validate_json(
            content
        )
    )

    logger.info(
        "Completed Groq call [fast_scoring] "
        "in %.2fs overall_score=%s",
        time.perf_counter()
        - started_at,
        result
        .overall_role_alignment
        .score,
    )

    expected = {
        "document_health":
            local_context[
                "document_diagnostics"
            ]
            is not None,

        "skills_alignment":
            local_context[
                "skills_diagnostics"
            ]
            is not None,

        "experience_fit":
            local_context[
                "experience_diagnostics"
            ]
            is not None,

        "qualification_alignment":
            local_context[
                "qualification_diagnostics"
            ].applicable,
    }

    for (
        field,
        applicable,
    ) in expected.items():
        if (
            not applicable
            and getattr(
                result,
                field,
            )
            is not None
        ):
            raise ValueError(
                f"{field} must be null when diagnostics are not applicable."
            )

    return result


# --------------- ASSESSMENT MAPPING ---------------

def _assessment_dict(
    name: str,
    assessment:
        ScoreAssessment,
) -> dict:
    (
        score_key,
        risk_key,
        list_map,
    ) = ASSESSMENT_FIELDS[
        name
    ]

    factors = []

    for factor in (
        assessment.factors
    ):
        item = {
            "factor":
                factor.factor,

            "impact":
                factor.impact,

            "reason":
                factor.reason,
        }

        if name in {
            "document_health",
            "evidence_quality",
        }:
            item[
                "severity"
            ] = (
                factor
                .impact_strength
            )

        else:
            item[
                "impact_strength"
            ] = (
                factor
                .impact_strength
            )

        if (
            name
            == "overall_role_alignment"
        ):
            item[
                "section"
            ] = (
                factor.section
                or
                "overall_role_alignment"
            )

        factors.append(
            item
        )

    output = {
        score_key:
            assessment.score,

        risk_key:
            assessment.risk,

        "rating":
            assessment.rating,

        "summary":
            assessment.summary,

        "primary_factors":
            factors,
    }

    for (
        source,
        target,
    ) in list_map.items():
        output[
            target
        ] = getattr(
            assessment,
            source,
        )

    return output


# --------------- SECTION ASSEMBLY ---------------

def assemble_sections(
    foundation:
        FoundationResponse,

    local_context:
        dict,

    scores:
        ScoringResponse,
) -> dict:
    assessments = {
        name: (
            _assessment_dict(
                name,
                getattr(
                    scores,
                    name,
                ),
            )
            if getattr(
                scores,
                name,
            )
            is not None
            else None
        )
        for name
        in ASSESSMENT_FIELDS
    }

    evidence = local_context[
        "evidence"
    ]

    qualification = (
        local_context[
            "qualification_diagnostics"
        ]
    )

    overall_score = (
        assessments[
            "overall_role_alignment"
        ][
            "overall_role_alignment_score"
        ]
    )

    sections = {
        "feedback": {
            "match_percentage":
                overall_score,

            "strengths": [
                item.requirement
                for item
                in evidence
                if (
                    item.status
                    == EvidenceStatus.SUPPORTED
                )
            ],

            "weaknesses": [
                item.requirement
                for item
                in evidence
                if (
                    item.status
                    != EvidenceStatus.SUPPORTED
                )
            ],

            "suggestions": (
                scores
                .overall_role_alignment
                .improvements
                or foundation.suggestions
            ),

            "requirements": [
                item.model_dump(
                    mode="json"
                )
                for item
                in evidence
            ],
        },

        "requirement_importance":
            local_context[
                "importance"
            ].model_dump(
                mode="json"
            ),

        "evidence_quality": {
            "diagnostics":
                local_context[
                    "evidence_diagnostics"
                ].model_dump(
                    mode="json"
                ),

            "assessment":
                assessments[
                    "evidence_quality"
                ],
        },

        "qualification_alignment": {
            "applicable":
                qualification.applicable,

            "diagnostics":
                qualification.model_dump(
                    mode="json"
                ),

            "assessment":
                assessments[
                    "qualification_alignment"
                ],
        },

        "project_relevance": {
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
                ].model_dump(
                    mode="json"
                ),

            "assessment":
                assessments[
                    "project_relevance"
                ],
        },

        "overall_role_alignment":
            assessments[
                "overall_role_alignment"
            ],
    }

    if local_context[
        "skills_diagnostics"
    ]:
        sections[
            "skills_alignment"
        ] = {
            "diagnostics":
                local_context[
                    "skills_diagnostics"
                ].model_dump(
                    mode="json"
                ),

            "assessment":
                assessments[
                    "skills_alignment"
                ],
        }

    if local_context[
        "experience_diagnostics"
    ]:
        sections[
            "experience_fit"
        ] = {
            "diagnostics":
                local_context[
                    "experience_diagnostics"
                ].model_dump(
                    mode="json"
                ),

            "assessment":
                assessments[
                    "experience_fit"
                ],
        }

    if local_context[
        "document_diagnostics"
    ]:
        sections[
            "document_health"
        ] = {
            "diagnostics":
                local_context[
                    "document_diagnostics"
                ].model_dump(
                    mode="json"
                ),

            "assessment":
                assessments[
                    "document_health"
                ],
        }

    return sections
