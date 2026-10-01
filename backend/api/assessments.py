"""Standalone assessments; these routes are not called by the full-analysis pipeline.

Synchronous handlers let FastAPI run blocking evaluators in its worker pool.
"""
from fastapi import APIRouter

from api.errors import evaluation_errors
from core.document_health_evaluator import evaluate_document_health
from core.evidence_quality import build_evidence_diagnostics
from core.evidence_quality_evaluator import evaluate_evidence_quality
from core.experience_fit import build_experience_fit_diagnostics
from core.experience_fit_evaluator import evaluate_experience_fit
from core.project_relevance import build_project_relevance_report
from core.qualification_alignment import build_qualification_diagnostics
from core.qualification_evaluator import evaluate_qualification_alignment
from core.requirement_importance_evaluator import evaluate_requirement_importance
from core.skills_alignment import build_skills_alignment_diagnostics
from core.skills_alignment_evaluator import evaluate_skills_alignment
from core.schemas import (
    DocumentHealthAssessment, ResumeDiagnosticsReport,
    EvidenceQualityRequest, EvidenceQualityReport,
    ExperienceFitRequest, ExperienceFitReport,
    ProjectRelevanceRequest, ProjectRelevanceReport,
    QualificationRequest, QualificationReport,
    RequirementImportanceRequest, RequirementImportanceReport,
    SkillsAlignmentRequest, SkillsAlignmentReport,
)

router = APIRouter()


@router.post('/resume/document-health/score', response_model=DocumentHealthAssessment)
def score_document_health(diagnostics: ResumeDiagnosticsReport):
    with evaluation_errors('Unable to evaluate document health.', validation_errors=False):
        return evaluate_document_health(diagnostics)


@router.post('/resume/evidence-quality', response_model=EvidenceQualityReport)
def evidence_quality(request: EvidenceQualityRequest):
    diagnostics = build_evidence_diagnostics(request.requirements)
    with evaluation_errors('Unable to evaluate evidence quality.', validation_errors=False):
        assessment = evaluate_evidence_quality(diagnostics)
    return EvidenceQualityReport(diagnostics=diagnostics, assessment=assessment)


@router.post('/job/requirement-importance', response_model=RequirementImportanceReport)
def requirement_importance(request: RequirementImportanceRequest):
    with evaluation_errors('Unable to evaluate requirement importance.'):
        return evaluate_requirement_importance(request)


@router.post('/resume/skills-alignment', response_model=SkillsAlignmentReport)
def skills_alignment(request: SkillsAlignmentRequest):
    with evaluation_errors('Unable to evaluate skills alignment.'):
        diagnostics = build_skills_alignment_diagnostics(
            request.evidence_requirements, request.requirement_profile,
        )
        assessment = evaluate_skills_alignment(diagnostics)
        return SkillsAlignmentReport(diagnostics=diagnostics, assessment=assessment)


@router.post('/resume/experience-fit', response_model=ExperienceFitReport)
def experience_fit(request: ExperienceFitRequest):
    with evaluation_errors('Unable to evaluate experience fit.'):
        diagnostics = build_experience_fit_diagnostics(
            request.evidence_requirements, request.requirement_profile,
        )
        assessment = evaluate_experience_fit(diagnostics)
        return ExperienceFitReport(diagnostics=diagnostics, assessment=assessment)


@router.post('/resume/qualification-alignment', response_model=QualificationReport)
def qualification_alignment(request: QualificationRequest):
    with evaluation_errors('Unable to evaluate qualifications.'):
        diagnostics = build_qualification_diagnostics(
            request.evidence_requirements, request.requirement_profile,
        )
        assessment = evaluate_qualification_alignment(diagnostics) if diagnostics.applicable else None
        return QualificationReport(
            applicable=diagnostics.applicable, diagnostics=diagnostics, assessment=assessment,
        )


@router.post('/resume/project-relevance', response_model=ProjectRelevanceReport)
def project_relevance(request: ProjectRelevanceRequest):
    with evaluation_errors('Unable to evaluate project relevance.'):
        return build_project_relevance_report(request)
