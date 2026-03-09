from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.routers.auth import get_current_user, User


router = APIRouter(prefix="/jobs", tags=["jobs"])


class JobRole(BaseModel):
    id: int
    title: str
    company: str
    location: str
    match_score: int


class JobRecommendationsResponse(BaseModel):
    target_role: str
    recommendations: list[JobRole]


@router.get("/recommendations", response_model=JobRecommendationsResponse)
async def get_job_recommendations(
    current_user: User = Depends(get_current_user),
) -> JobRecommendationsResponse:
    return JobRecommendationsResponse(
        target_role="Software Engineer",
        recommendations=[
            JobRole(
                id=1,
                title="Backend Engineer",
                company="TechNova",
                location="Remote",
                match_score=88,
            ),
            JobRole(
                id=2,
                title="Full-Stack Developer",
                company="Product Labs",
                location="Hybrid",
                match_score=81,
            ),
        ],
    )

