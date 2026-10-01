"""One structured provider request, followed by deterministic report assembly."""
import json
from collections import Counter
from typing import Literal

from pydantic import Field, model_validator

from core.llm import client, config
from core.prompts import load_prompt
from core.schemas import (
    StrictModel, RequirementEvaluation, RequirementImportanceItem,
    RequirementImportance, RequirementCategory, EvidenceStatus,
    DocumentHealthAssessment, EvidenceQualityAssessment, SkillsAlignmentAssessment,
    ExperienceFitAssessment, QualificationAssessment, ProjectRelevanceAssessment,
    OverallRoleAlignmentAssessment, ResumeProject, RequirementImportanceReport,
)
from core.evidence_quality import build_evidence_diagnostics
from core.skills_alignment import build_skills_alignment_diagnostics
from core.experience_fit import build_experience_fit_diagnostics
from core.qualification_alignment import build_qualification_diagnostics
from core.project_diagnostics import build_project_diagnostics


class UnifiedRequirement(RequirementEvaluation):
    importance: RequirementImportance
    category: RequirementCategory
    jd_signal: str
    reason: str


class UnifiedAnalysis(StrictModel):
    match_percentage: int = Field(ge=0, le=100)
    requirements: list[UnifiedRequirement] = Field(min_length=1)
    suggestions: list[str]
    projects: list[ResumeProject]
    document_health: DocumentHealthAssessment | None
    evidence_quality: EvidenceQualityAssessment
    skills_alignment: SkillsAlignmentAssessment | None
    experience_fit: ExperienceFitAssessment | None
    qualification_alignment: QualificationAssessment | None
    project_relevance: ProjectRelevanceAssessment
    overall_role_alignment: OverallRoleAlignmentAssessment

    @model_validator(mode='after')
    def validate_requirements(self):
        names = [item.requirement.strip().casefold() for item in self.requirements]
        if not all(names) or len(set(names)) != len(names):
            raise ValueError('Requirements must be nonempty and unique.')
        for item in self.requirements:
            if item.status == EvidenceStatus.NOT_EVIDENCED and item.evidence is not None:
                raise ValueError('Unevidenced requirements must have null evidence.')
            if item.status != EvidenceStatus.NOT_EVIDENCED and not (item.evidence or '').strip():
                raise ValueError('Supported and partial requirements need resume evidence.')
        categories = {item.category for item in self.requirements}
        for field, applicable in (
            ('skills_alignment', RequirementCategory.SKILL in categories),
            ('experience_fit', bool(categories & {RequirementCategory.EXPERIENCE, RequirementCategory.RESPONSIBILITY})),
            ('qualification_alignment', bool(categories & {RequirementCategory.EDUCATION, RequirementCategory.CERTIFICATION})),
        ):
            if (getattr(self, field) is not None) != applicable:
                raise ValueError(f'{field} must match the requirement categories.')
        return self


ASSESSMENT_FIELDS = {
    'document_health': ('document_health_score', 'processing_risk', {'gaps': 'critical_issues'}),
    'evidence_quality': ('evidence_quality_score', 'evidence_risk', {'partial': 'weak_evidence_requirements', 'gaps': 'unevidenced_requirements'}),
    'skills_alignment': ('skills_alignment_score', 'alignment_risk', {'strengths': 'core_requirements_satisfied', 'partial': 'partial_requirements', 'gaps': 'missing_critical_requirements'}),
    'experience_fit': ('experience_fit_score', 'experience_risk', {'strengths': 'core_experience_satisfied', 'partial': 'partial_experience_requirements', 'gaps': 'missing_critical_experience'}),
    'qualification_alignment': ('qualification_score', 'qualification_risk', {'strengths': 'satisfied_qualifications', 'partial': 'partial_qualifications', 'gaps': 'missing_critical_qualifications'}),
    'project_relevance': ('projects_relevance_score', 'project_fit_risk', {'strengths': 'strongest_projects', 'partial': 'partially_relevant_projects', 'gaps': 'missing_project_evidence'}),
    'overall_role_alignment': ('overall_role_alignment_score', 'screening_risk', {'strengths': 'strongest_alignment_areas', 'gaps': 'critical_gaps', 'improvements': 'priority_improvements'}),
}


class AssessmentFactor(StrictModel):
    factor: str
    impact: Literal['positive', 'negative', 'neutral']
    impact_strength: Literal['low', 'medium', 'high']
    reason: str


class Assessment(StrictModel):
    score: int = Field(ge=0, le=100)
    rating: Literal['excellent', 'strong', 'good', 'fair', 'weak']
    risk: Literal['low', 'moderate', 'high', 'severe']
    summary: str
    factors: list[AssessmentFactor]
    strengths: list[str]
    partial: list[str]
    gaps: list[str]
    improvements: list[str]


class Assessments(StrictModel):
    document_health: Assessment | None
    evidence_quality: Assessment
    skills_alignment: Assessment | None
    experience_fit: Assessment | None
    qualification_alignment: Assessment | None
    project_relevance: Assessment
    overall_role_alignment: Assessment


class UnifiedResponse(StrictModel):
    match_percentage: int = Field(ge=0, le=100)
    requirements: list[UnifiedRequirement] = Field(min_length=1)
    suggestions: list[str]
    projects: list[ResumeProject]
    assessments: Assessments

    def to_analysis(self) -> UnifiedAnalysis:
        output = self.model_dump(mode='json', exclude={'assessments'})
        output.update({name: None for name in ASSESSMENT_FIELDS})
        for name in ASSESSMENT_FIELDS:
            assessment = getattr(self.assessments, name)
            if assessment is None:
                continue
            score_key, risk_key, lists = ASSESSMENT_FIELDS[name]
            factors = []
            for factor in assessment.factors:
                value = factor.model_dump()
                if name == 'overall_role_alignment':
                    value['section'] = name
                if name in {'document_health', 'evidence_quality'}:
                    value['severity'] = value.pop('impact_strength')
                factors.append(value)
            output[name] = {
                score_key: assessment.score, risk_key: assessment.risk,
                'rating': assessment.rating, 'summary': assessment.summary,
                'primary_factors': factors,
                **{target: getattr(assessment, source) for source, target in lists.items()},
            }
        return UnifiedAnalysis.model_validate(output)


# A uniform assessment shape avoids seven almost-identical provider schemas.
UNIFIED_RESPONSE_SCHEMA = UnifiedResponse.model_json_schema()


def generate_unified_analysis(resume_text: str, jd_text: str, document_diagnostics=None) -> UnifiedAnalysis:
    if not resume_text.strip() or not jd_text.strip():
        raise ValueError('Resume and job description must contain readable text.')
    settings = config['llm']['unified_analysis']
    if len(resume_text) + len(jd_text) > settings['max_input_characters']:
        raise ValueError('Resume and job description are too long. Please shorten them and retry.')
    prompt = load_prompt('unified_analysis')
    payload = {
        'resume_text': resume_text,
        'job_description': jd_text,
        'document_diagnostics': document_diagnostics.model_dump(mode='json') if document_diagnostics else None,
    }
    # No automatic retry, repair request, or fallback: one provider attempt per analysis.
    response = client.with_options(max_retries=0, timeout=settings['timeout_seconds']).chat.completions.create(
        model=settings['model'],
        temperature=settings['temperature'],
        reasoning_effort=settings['reasoning_effort'],
        include_reasoning=False,
        max_completion_tokens=settings['max_completion_tokens'],
        messages=[
            {'role': 'system', 'content': prompt['system_prompt'] + '\nRequired output schema (include every nested required field):\n' + json.dumps(UNIFIED_RESPONSE_SCHEMA, separators=(',', ':'))},
            {'role': 'user', 'content': json.dumps(payload, ensure_ascii=False)},
        ],
        response_format={'type': 'json_object'},
    )
    choice = response.choices[0]
    if choice.finish_reason != 'stop' or not choice.message.content:
        raise RuntimeError('The analysis response was incomplete. Please retry.')
    result = UnifiedResponse.model_validate_json(choice.message.content).to_analysis()
    if (result.document_health is not None) != (document_diagnostics is not None):
        raise ValueError('Document health must match the available PDF diagnostics.')
    return result


def assemble_sections(result: UnifiedAnalysis, document_diagnostics=None) -> dict:
    """Preserve the report API; derive all counts and diagnostic scores locally."""
    evidence = [RequirementEvaluation.model_validate({
        key: getattr(item, key) for key in RequirementEvaluation.model_fields
    }) for item in result.requirements]
    profile = [RequirementImportanceItem.model_validate({
        key: getattr(item, key) for key in RequirementImportanceItem.model_fields
    }) for item in result.requirements]
    counts = Counter(item.importance.value.lower() for item in profile)
    importance = RequirementImportanceReport(
        total_requirements=len(profile), requirements=profile,
        **{name: counts[name] for name in ('mandatory', 'high_priority', 'preferred', 'optional')},
    )
    qualification = build_qualification_diagnostics(evidence, profile)
    sections = {
        'feedback': {
            'match_percentage': result.match_percentage,
            'requirements': [item.model_dump(mode='json') for item in evidence],
            'strengths': [item.requirement for item in evidence if item.status == EvidenceStatus.SUPPORTED],
            'weaknesses': [item.requirement for item in evidence if item.status != EvidenceStatus.SUPPORTED],
            'suggestions': result.suggestions,
        },
        'requirement_importance': importance.model_dump(mode='json'),
        'evidence_quality': {
            'diagnostics': build_evidence_diagnostics(evidence).model_dump(mode='json'),
            'assessment': result.evidence_quality.model_dump(mode='json'),
        },
        'qualification_alignment': {
            'applicable': qualification.applicable,
            'diagnostics': qualification.model_dump(mode='json'),
            'assessment': result.qualification_alignment.model_dump(mode='json') if result.qualification_alignment else None,
        },
        'project_relevance': {
            'projects': [item.model_dump(mode='json') for item in result.projects],
            'diagnostics': build_project_diagnostics(result.projects).model_dump(mode='json'),
            'assessment': result.project_relevance.model_dump(mode='json'),
        },
        'overall_role_alignment': result.overall_role_alignment.model_dump(mode='json'),
    }
    for name, assessment, builder in (
        ('skills_alignment', result.skills_alignment, build_skills_alignment_diagnostics),
        ('experience_fit', result.experience_fit, build_experience_fit_diagnostics),
    ):
        if assessment is not None:
            sections[name] = {
                'diagnostics': builder(evidence, profile).model_dump(mode='json'),
                'assessment': assessment.model_dump(mode='json'),
            }
    if document_diagnostics is not None and result.document_health is not None:
        sections['document_health'] = {
            'diagnostics': document_diagnostics.model_dump(mode='json'),
            'assessment': result.document_health.model_dump(mode='json'),
        }
    return sections
