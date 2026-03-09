from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.integration_schema import CareerSupportRequest
from app.schemas.roadmap_schema import CareerRoadmapResponse, CareerTransitionPlanRequest, CareerTransitionPlanResponse
from app.services.career_service import build_transition_plan, generate_roadmap, list_transition_plans


router = APIRouter(prefix="/career", tags=["Career"])


@router.get("/health")
def career_health(_: User = Depends(get_current_user)) -> dict[str, str]:
    return {"message": "Career router ready"}


@router.post("/support")
def career_support(payload: CareerSupportRequest, _: User = Depends(get_current_user)) -> dict:
    return generate_roadmap(
        goal=payload.goal,
        background=payload.background,
        target_role=payload.target_role,
        constraints=payload.constraints,
    )


@router.post("/plan", response_model=CareerTransitionPlanResponse)
def create_transition_plan(
    payload: CareerTransitionPlanRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CareerTransitionPlanResponse:
    result = build_transition_plan(
        db=db,
        user_id=user.id,
        target_role=payload.target_role,
        current_skills=payload.current_skills,
        experience_summary=payload.experience_summary,
        resume_summary=payload.resume_summary,
        available_hours_per_week=payload.available_hours_per_week,
        timeline_weeks=payload.timeline_weeks,
    )
    return CareerTransitionPlanResponse(**result)


@router.get("/roadmaps", response_model=list[CareerRoadmapResponse])
def get_roadmaps(
    limit: int = 20,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[CareerRoadmapResponse]:
    rows = list_transition_plans(db=db, user_id=user.id, limit=limit)
    return [CareerRoadmapResponse(**row) for row in rows]
