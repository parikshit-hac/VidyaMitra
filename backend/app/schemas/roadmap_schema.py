from datetime import datetime

from pydantic import BaseModel, Field


class RoadmapSummary(BaseModel):
    id: str
    goal: str


class CareerTransitionPlanRequest(BaseModel):
    target_role: str = Field(min_length=2, max_length=120)
    current_skills: list[str] = Field(default_factory=list)
    experience_summary: str = Field(default="", max_length=3000)
    resume_summary: str = Field(default="", max_length=3000)
    available_hours_per_week: int = Field(default=8, ge=1, le=80)
    timeline_weeks: int = Field(default=12, ge=4, le=52)


class CareerTransitionPlanResponse(BaseModel):
    roadmap_id: str
    target_role: str
    transferable_strengths: list[str]
    skill_gaps: list[str]
    recommended_certifications: list[str]
    learning_path: list[dict]
    weekly_plan: list[dict]
    notes: str
    created_at: datetime | None = None


class CareerRoadmapResponse(BaseModel):
    id: str
    goal: str
    milestones: dict
    created_at: datetime
