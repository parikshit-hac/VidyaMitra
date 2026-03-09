from pydantic import BaseModel, Field


class ResumeBuildRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    target_role: str = Field(min_length=2, max_length=120)
    professional_summary: str = Field(default="", max_length=2000)
    skills: list[str] = Field(default_factory=list)
    experiences: list[str] = Field(default_factory=list)
    projects: list[str] = Field(default_factory=list)
    education: list[str] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)


class ResumeBuildResponse(BaseModel):
    full_name: str
    target_role: str
    headline: str
    summary: str
    skills: list[str]
    experience_bullets: list[str]
    projects: list[str]
    education: list[str]
    certifications: list[str]
    ats_keywords: list[str]
    ai_source: str


class EligibilityCriteriaRequest(BaseModel):
    target_role: str = Field(min_length=2, max_length=120)
    current_skills: list[str] = Field(default_factory=list)
    years_experience: float = Field(default=0.0, ge=0.0, le=50.0)
    education_level: str = Field(default="bachelor", max_length=80)


class EligibilityCriteriaResponse(BaseModel):
    target_role: str
    eligibility_score: int
    matched_skills: list[str]
    missing_skills: list[str]
    skill_breakdown: list[dict] = Field(default_factory=list)
    improvement_areas: list[dict] = Field(default_factory=list)
    criteria_breakdown: dict
    recommendations: list[str]


class GeneralEvaluationRequest(BaseModel):
    category: str = Field(default="resume", max_length=80)
    content: str = Field(min_length=20, max_length=12000)
    target_role: str = Field(default="", max_length=120)


class GeneralEvaluationResponse(BaseModel):
    category: str
    score: int
    strengths: list[str]
    improvements: list[str]
    next_steps: list[str]
