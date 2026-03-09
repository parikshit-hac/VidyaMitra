from fastapi import APIRouter, Depends

from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.evaluation_schema import (
    EligibilityCriteriaRequest,
    EligibilityCriteriaResponse,
    GeneralEvaluationRequest,
    GeneralEvaluationResponse,
    ResumeBuildRequest,
    ResumeBuildResponse,
)
from app.services.evaluation_service import build_resume_draft, eligibility_assessment, evaluate_content


router = APIRouter(prefix="/evaluate", tags=["Evaluate"])


@router.post("/resume-build", response_model=ResumeBuildResponse)
def resume_build(payload: ResumeBuildRequest, _: User = Depends(get_current_user)) -> ResumeBuildResponse:
    result = build_resume_draft(
        full_name=payload.full_name,
        target_role=payload.target_role,
        professional_summary=payload.professional_summary,
        skills=payload.skills,
        experiences=payload.experiences,
        projects=payload.projects,
        education=payload.education,
        certifications=payload.certifications,
    )
    return ResumeBuildResponse(**result)


@router.post("/eligibility", response_model=EligibilityCriteriaResponse)
def eligibility(payload: EligibilityCriteriaRequest, _: User = Depends(get_current_user)) -> EligibilityCriteriaResponse:
    result = eligibility_assessment(
        target_role=payload.target_role,
        current_skills=payload.current_skills,
        years_experience=payload.years_experience,
        education_level=payload.education_level,
    )
    return EligibilityCriteriaResponse(**result)


@router.post("/content", response_model=GeneralEvaluationResponse)
def content_eval(payload: GeneralEvaluationRequest, _: User = Depends(get_current_user)) -> GeneralEvaluationResponse:
    result = evaluate_content(
        category=payload.category,
        content=payload.content,
        target_role=payload.target_role,
    )
    return GeneralEvaluationResponse(**result)
