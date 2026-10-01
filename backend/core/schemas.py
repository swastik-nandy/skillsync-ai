from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


# --------------- BASE MODEL ---------------

class StrictModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )


# --------------- EVIDENCE STATUS ---------------

class EvidenceStatus(str, Enum):
    SUPPORTED = "SUPPORTED"
    PARTIAL = "PARTIAL"
    NOT_EVIDENCED = "NOT_EVIDENCED"


# --------------- REQUIREMENT ---------------

class RequirementEvaluation(StrictModel):
    requirement: str
    status: EvidenceStatus
    evidence: str | None


# --------------- FEEDBACK ---------------

class FeedbackReport(StrictModel):
    match_percentage: int = Field(
        ge=0,
        le=100,
    )

    requirements: list[RequirementEvaluation]

    suggestions: list[str]


# --------------- RESPONSE SCHEMA ---------------

FEEDBACK_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "match_percentage": {
            "type": "integer",
        },
        "requirements": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "requirement": {
                        "type": "string",
                    },
                    "status": {
                        "type": "string",
                        "enum": [
                            "SUPPORTED",
                            "PARTIAL",
                            "NOT_EVIDENCED",
                        ],
                    },
                    "evidence": {
                        "type": [
                            "string",
                            "null",
                        ],
                    },
                },
                "required": [
                    "requirement",
                    "status",
                    "evidence",
                ],
                "additionalProperties": False,
            },
        },
        "suggestions": {
            "type": "array",
            "items": {
                "type": "string",
            },
        },
    },
    "required": [
        "match_percentage",
        "requirements",
        "suggestions",
    ],
    "additionalProperties": False,
}


class ResumeParseReport(StrictModel):
    filename: str
    file_type: str
    parse_percentage: int = Field(
        ge=0,
        le=100,
    )
    parsed_units: int = Field(
        ge=0,
    )
    total_units: int = Field(
        ge=0,
    )
    unit: str
    characters_extracted: int = Field(
        ge=0,
    )
    warning: str | None = None


class StructureBreakdown(StrictModel):
    section_structure: int = Field(
        ge=0,
        le=35,
    )
    layout: int = Field(
        ge=0,
        le=25,
    )
    font_consistency: int = Field(
        ge=0,
        le=15,
    )
    page_consistency: int = Field(
        ge=0,
        le=10,
    )
    text_density: int = Field(
        ge=0,
        le=10,
    )
    parsability: int = Field(
        ge=0,
        le=5,
    )


class ParsabilityBreakdown(StrictModel):
    extraction_coverage: int = Field(
        ge=0,
        le=30,
    )
    text_integrity: int = Field(
        ge=0,
        le=15,
    )
    reading_order: int = Field(
        ge=0,
        le=20,
    )
    fragmentation: int = Field(
        ge=0,
        le=15,
    )
    orientation: int = Field(
        ge=0,
        le=10,
    )
    ocr_independence: int = Field(
        ge=0,
        le=10,
    )


class ResumeDiagnosticsReport(StrictModel):
    filename: str
    file_type: str
    file_size_bytes: int = Field(
        ge=0,
    )

    total_pages: int = Field(
        ge=0,
    )
    parsed_pages: int = Field(
        ge=0,
    )
    scanned_pages: int = Field(
        ge=0,
    )

    parse_percentage: int = Field(
        ge=0,
        le=100,
    )

    text_layer: bool
    ocr_required: bool

    characters_extracted: int = Field(
        ge=0,
    )
    words_extracted: int = Field(
        ge=0,
    )
    average_words_per_page: float = Field(
        ge=0,
    )

    links: int = Field(
        ge=0,
    )
    embedded_images: int = Field(
        ge=0,
    )

    font_families: list[str]
    font_sizes: list[float]
    body_font_size: float | None

    page_sizes_consistent: bool

    layout_complexity: str
    multi_column_pages: int = Field(
        ge=0,
    )

    sections_detected: list[str]

    structure_friendliness: int = Field(
        ge=0,
        le=100,
    )

    technical_parsability: int = Field(
        ge=0,
        le=100,
    )

    deterministic_health_index: int = Field(
        ge=0,
        le=100,
    )

    deterministic_health_label: str


    parsability_breakdown: ParsabilityBreakdown

    reading_order_complexity: str
    fragmentation: str

    blocks_per_100_words: float = Field(
        ge=0,
    )

    non_horizontal_text_percentage: float = Field(
        ge=0,
        le=100,
    )

    overlapping_block_percentage: float = Field(
        ge=0,
        le=100,
    )

    suspicious_character_percentage: float = Field(
        ge=0,
        le=100,
    )

    max_columns_detected: int = Field(
        ge=1,
    )

    mixed_layout_pages: int = Field(
        ge=0,
    )


    structure_breakdown: StructureBreakdown
    observations: list[str]


class DocumentHealthImpact(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


class DocumentHealthSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class DocumentHealthFactor(StrictModel):
    factor: str
    impact: DocumentHealthImpact
    severity: DocumentHealthSeverity
    reason: str


class DocumentHealthAssessment(StrictModel):
    document_health_score: int = Field(
        ge=0,
        le=100,
    )
    rating: str
    processing_risk: str
    summary: str
    primary_factors: list[DocumentHealthFactor]
    critical_issues: list[str]


class EvidenceRequirementDiagnostic(StrictModel):
    requirement: str
    status: EvidenceStatus
    evidence: str | None
    has_evidence: bool
    evidence_characters: int = Field(
        ge=0,
    )


class EvidenceDiagnostics(StrictModel):
    total_requirements: int = Field(
        ge=0,
    )

    supported: int = Field(
        ge=0,
    )
    partial: int = Field(
        ge=0,
    )
    not_evidenced: int = Field(
        ge=0,
    )

    supported_percentage: float = Field(
        ge=0,
        le=100,
    )
    partial_percentage: float = Field(
        ge=0,
        le=100,
    )
    not_evidenced_percentage: float = Field(
        ge=0,
        le=100,
    )

    requirements_with_evidence: int = Field(
        ge=0,
    )
    evidence_coverage_percentage: float = Field(
        ge=0,
        le=100,
    )

    status_evidence_mismatches: int = Field(
        ge=0,
    )

    deterministic_evidence_index: int = Field(
        ge=0,
        le=100,
    )

    requirements: list[EvidenceRequirementDiagnostic]


class EvidenceQualityImpact(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


class EvidenceQualitySeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class EvidenceQualityFactor(StrictModel):
    factor: str
    impact: EvidenceQualityImpact
    severity: EvidenceQualitySeverity
    reason: str


class EvidenceQualityAssessment(StrictModel):
    evidence_quality_score: int = Field(
        ge=0,
        le=100,
    )

    rating: str
    evidence_risk: str
    summary: str

    primary_factors: list[EvidenceQualityFactor]
    weak_evidence_requirements: list[str]
    unevidenced_requirements: list[str]


class EvidenceQualityRequest(StrictModel):
    requirements: list[RequirementEvaluation]


class EvidenceQualityReport(StrictModel):
    diagnostics: EvidenceDiagnostics
    assessment: EvidenceQualityAssessment


class RequirementImportance(str, Enum):
    MANDATORY = "MANDATORY"
    HIGH_PRIORITY = "HIGH_PRIORITY"
    PREFERRED = "PREFERRED"
    OPTIONAL = "OPTIONAL"


class RequirementCategory(str, Enum):
    SKILL = "SKILL"
    EXPERIENCE = "EXPERIENCE"
    EDUCATION = "EDUCATION"
    CERTIFICATION = "CERTIFICATION"
    RESPONSIBILITY = "RESPONSIBILITY"
    OTHER = "OTHER"


class RequirementImportanceItem(StrictModel):
    requirement: str
    importance: RequirementImportance
    category: RequirementCategory
    jd_signal: str
    reason: str


class RequirementImportanceRequest(StrictModel):
    jd_text: str
    requirements: list[str]


class RequirementImportanceEvaluation(StrictModel):
    requirements: list[RequirementImportanceItem]


class RequirementImportanceReport(StrictModel):
    total_requirements: int = Field(
        ge=0,
    )
    mandatory: int = Field(
        ge=0,
    )
    high_priority: int = Field(
        ge=0,
    )
    preferred: int = Field(
        ge=0,
    )
    optional: int = Field(
        ge=0,
    )
    requirements: list[RequirementImportanceItem]


class SkillAlignmentRequirement(StrictModel):
    requirement: str
    importance: RequirementImportance
    status: EvidenceStatus
    evidence: str | None
    jd_signal: str


class SkillAlignmentDiagnostics(StrictModel):
    total_skill_requirements: int = Field(
        ge=0,
    )

    supported: int = Field(
        ge=0,
    )
    partial: int = Field(
        ge=0,
    )
    not_evidenced: int = Field(
        ge=0,
    )

    mandatory_count: int = Field(
        ge=0,
    )
    high_priority_count: int = Field(
        ge=0,
    )
    preferred_count: int = Field(
        ge=0,
    )
    optional_count: int = Field(
        ge=0,
    )

    mandatory_coverage_score: int | None = Field(
        default=None,
        ge=0,
        le=100,
    )

    high_priority_coverage_score: int | None = Field(
        default=None,
        ge=0,
        le=100,
    )

    preferred_coverage_score: int | None = Field(
        default=None,
        ge=0,
        le=100,
    )

    optional_coverage_score: int | None = Field(
        default=None,
        ge=0,
        le=100,
    )

    evidence_strength_score: int = Field(
        ge=0,
        le=100,
    )

    missing_mandatory: list[str]
    missing_high_priority: list[str]
    partial_mandatory: list[str]
    partial_high_priority: list[str]

    requirements: list[SkillAlignmentRequirement]


class SkillsAlignmentImpact(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


class SkillsAlignmentFactor(StrictModel):
    factor: str
    impact: SkillsAlignmentImpact
    impact_strength: str
    reason: str


class SkillsAlignmentAssessment(StrictModel):
    skills_alignment_score: int = Field(
        ge=0,
        le=100,
    )

    rating: str
    alignment_risk: str
    summary: str

    primary_factors: list[SkillsAlignmentFactor]

    core_requirements_satisfied: list[str]
    partial_requirements: list[str]
    missing_critical_requirements: list[str]


class SkillsAlignmentRequest(StrictModel):
    evidence_requirements: list[RequirementEvaluation]
    requirement_profile: list[RequirementImportanceItem]


class SkillsAlignmentReport(StrictModel):
    diagnostics: SkillAlignmentDiagnostics
    assessment: SkillsAlignmentAssessment


class ExperienceFitRequirement(StrictModel):
    requirement: str
    category: RequirementCategory
    importance: RequirementImportance
    status: EvidenceStatus
    evidence: str | None
    jd_signal: str


class ExperienceFitDiagnostics(StrictModel):
    total_requirements: int = Field(
        ge=0,
    )

    experience_requirements: int = Field(
        ge=0,
    )

    responsibility_requirements: int = Field(
        ge=0,
    )

    supported: int = Field(
        ge=0,
    )

    partial: int = Field(
        ge=0,
    )

    not_evidenced: int = Field(
        ge=0,
    )

    mandatory_count: int = Field(
        ge=0,
    )

    high_priority_count: int = Field(
        ge=0,
    )

    preferred_count: int = Field(
        ge=0,
    )

    optional_count: int = Field(
        ge=0,
    )

    mandatory_coverage_score: int | None = Field(
        default=None,
        ge=0,
        le=100,
    )

    high_priority_coverage_score: int | None = Field(
        default=None,
        ge=0,
        le=100,
    )

    responsibility_coverage_score: int | None = Field(
        default=None,
        ge=0,
        le=100,
    )

    experience_coverage_score: int | None = Field(
        default=None,
        ge=0,
        le=100,
    )

    evidence_coverage_score: int = Field(
        ge=0,
        le=100,
    )

    missing_mandatory: list[str]
    missing_high_priority: list[str]

    partial_mandatory: list[str]
    partial_high_priority: list[str]

    requirements: list[ExperienceFitRequirement]


class ExperienceFitImpact(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


class ExperienceFitFactor(StrictModel):
    factor: str
    impact: ExperienceFitImpact
    impact_strength: str
    reason: str


class ExperienceFitAssessment(StrictModel):
    experience_fit_score: int = Field(
        ge=0,
        le=100,
    )

    rating: str
    experience_risk: str
    summary: str

    primary_factors: list[ExperienceFitFactor]

    core_experience_satisfied: list[str]
    partial_experience_requirements: list[str]
    missing_critical_experience: list[str]


class ExperienceFitRequest(StrictModel):
    evidence_requirements: list[RequirementEvaluation]
    requirement_profile: list[RequirementImportanceItem]


class ExperienceFitReport(StrictModel):
    diagnostics: ExperienceFitDiagnostics
    assessment: ExperienceFitAssessment


class QualificationRequirement(StrictModel):
    requirement: str
    category: RequirementCategory
    importance: RequirementImportance
    status: EvidenceStatus
    evidence: str | None
    jd_signal: str


class QualificationDiagnostics(StrictModel):
    applicable: bool

    total_requirements: int = Field(
        ge=0,
    )

    education_requirements: int = Field(
        ge=0,
    )

    certification_requirements: int = Field(
        ge=0,
    )

    supported: int = Field(
        ge=0,
    )

    partial: int = Field(
        ge=0,
    )

    not_evidenced: int = Field(
        ge=0,
    )

    mandatory_count: int = Field(
        ge=0,
    )

    high_priority_count: int = Field(
        ge=0,
    )

    preferred_count: int = Field(
        ge=0,
    )

    optional_count: int = Field(
        ge=0,
    )

    mandatory_coverage_score: int | None = Field(
        default=None,
        ge=0,
        le=100,
    )

    high_priority_coverage_score: int | None = Field(
        default=None,
        ge=0,
        le=100,
    )

    education_coverage_score: int | None = Field(
        default=None,
        ge=0,
        le=100,
    )

    certification_coverage_score: int | None = Field(
        default=None,
        ge=0,
        le=100,
    )

    missing_mandatory: list[str]
    missing_high_priority: list[str]
    partial_critical: list[str]

    requirements: list[QualificationRequirement]


class QualificationImpact(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


class QualificationFactor(StrictModel):
    factor: str
    impact: QualificationImpact
    impact_strength: str
    reason: str


class QualificationAssessment(StrictModel):
    qualification_score: int = Field(
        ge=0,
        le=100,
    )

    rating: str
    qualification_risk: str
    summary: str

    primary_factors: list[QualificationFactor]

    satisfied_qualifications: list[str]
    partial_qualifications: list[str]
    missing_critical_qualifications: list[str]


class QualificationRequest(StrictModel):
    evidence_requirements: list[RequirementEvaluation]
    requirement_profile: list[RequirementImportanceItem]


class QualificationReport(StrictModel):
    applicable: bool
    diagnostics: QualificationDiagnostics
    assessment: QualificationAssessment | None


class ResumeProject(StrictModel):
    name: str
    description: str
    technologies: list[str]
    responsibilities: list[str]
    outcomes: list[str]
    quantified_metrics: list[str]
    production_signals: list[str]
    evidence: list[str]


class ProjectExtractionResult(StrictModel):
    projects: list[ResumeProject]


class ProjectDiagnostic(StrictModel):
    name: str

    technology_count: int = Field(
        ge=0,
    )

    responsibility_count: int = Field(
        ge=0,
    )

    outcome_count: int = Field(
        ge=0,
    )

    quantified_metric_count: int = Field(
        ge=0,
    )

    production_signal_count: int = Field(
        ge=0,
    )

    evidence_completeness_score: int = Field(
        ge=0,
        le=100,
    )


class ProjectRelevanceDiagnostics(StrictModel):
    total_projects: int = Field(
        ge=0,
    )

    projects_with_technologies: int = Field(
        ge=0,
    )

    projects_with_outcomes: int = Field(
        ge=0,
    )

    projects_with_quantified_metrics: int = Field(
        ge=0,
    )

    projects_with_production_signals: int = Field(
        ge=0,
    )

    technology_evidence_score: int = Field(
        ge=0,
        le=100,
    )

    outcome_evidence_score: int = Field(
        ge=0,
        le=100,
    )

    quantified_impact_score: int = Field(
        ge=0,
        le=100,
    )

    production_depth_score: int = Field(
        ge=0,
        le=100,
    )

    project_evidence_score: int = Field(
        ge=0,
        le=100,
    )

    projects: list[ProjectDiagnostic]


class ProjectRelevanceImpact(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


class ProjectRelevanceFactor(StrictModel):
    factor: str
    impact: ProjectRelevanceImpact
    impact_strength: str
    reason: str


class ProjectRelevanceAssessment(StrictModel):
    projects_relevance_score: int = Field(
        ge=0,
        le=100,
    )

    rating: str
    project_fit_risk: str
    summary: str

    primary_factors: list[ProjectRelevanceFactor]

    strongest_projects: list[str]
    partially_relevant_projects: list[str]
    missing_project_evidence: list[str]


class ProjectRelevanceRequest(StrictModel):
    resume_text: str
    requirement_profile: list[RequirementImportanceItem]


class ProjectRelevanceReport(StrictModel):
    projects: list[ResumeProject]
    diagnostics: ProjectRelevanceDiagnostics
    assessment: ProjectRelevanceAssessment


class OverallAlignmentImpact(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


class OverallAlignmentFactor(StrictModel):
    factor: str
    section: str
    impact: OverallAlignmentImpact
    impact_strength: str
    reason: str


class OverallRoleAlignmentContext(StrictModel):
    requirement_profile: list[RequirementImportanceItem]
    evidence_requirements: list[RequirementEvaluation]

    evidence_quality: EvidenceQualityAssessment | None
    skills_alignment: SkillsAlignmentAssessment | None
    experience_fit: ExperienceFitAssessment | None
    qualification_alignment: QualificationAssessment | None
    projects_relevance: ProjectRelevanceAssessment | None


class OverallRoleAlignmentAssessment(StrictModel):
    overall_role_alignment_score: int = Field(
        ge=0,
        le=100,
    )

    rating: str
    screening_risk: str
    summary: str

    primary_factors: list[OverallAlignmentFactor]

    strongest_alignment_areas: list[str]
    critical_gaps: list[str]
    priority_improvements: list[str]
