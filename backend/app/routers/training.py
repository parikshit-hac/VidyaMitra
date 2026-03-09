from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.routers.auth import get_current_user, User


router = APIRouter(prefix="/training", tags=["training"])


class TrainingModule(BaseModel):
    id: int
    title: str
    difficulty: str
    duration_minutes: int
    completed: bool = False


class TrainingPlanResponse(BaseModel):
    target_role: str
    summary: str
    modules: list[TrainingModule]


@router.get("/plan", response_model=TrainingPlanResponse)
async def get_training_plan(current_user: User = Depends(get_current_user)) -> TrainingPlanResponse:
    return TrainingPlanResponse(
        target_role="Software Engineer",
        summary="Foundational plan to strengthen algorithms, systems design, and practical project skills.",
        modules=[
            TrainingModule(
                id=1,
                title="Algorithms & Data Structures Refresher",
                difficulty="Intermediate",
                duration_minutes=90,
            ),
            TrainingModule(
                id=2,
                title="System Design Fundamentals",
                difficulty="Intermediate",
                duration_minutes=120,
            ),
            TrainingModule(
                id=3,
                title="Full-Stack Project: API + React",
                difficulty="Advanced",
                duration_minutes=240,
            ),
        ],
    )

