from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ResumeSummary(BaseModel):
    id: UUID
    title: str | None = None


class ResumeUploadResponse(BaseModel):
    resume_id: UUID
    title: str
    file_url: str
    extracted_chars: int
    message: str


class ResumeAnalyzeRequest(BaseModel):
    target_role: str = Field(default="Data Analyst", min_length=2, max_length=120)


class ResumeAnalysisResponse(BaseModel):
    resume_id: UUID
    target_role: str
    identified_skills: list[str]
    skill_gaps: list[str]
    recommended_courses: list[dict]
    ai_summary: str
    ai_source: str
    updated_at: datetime | None = None


class ResumeDetailResponse(BaseModel):
    id: UUID
    title: str | None = None
    file_url: str | None = None
    is_active: bool | None = None
    metadata: dict
    created_at: datetime | None = None
    updated_at: datetime | None = None
