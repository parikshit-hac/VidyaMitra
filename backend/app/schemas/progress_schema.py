from datetime import datetime

from pydantic import BaseModel


class ProgressSummary(BaseModel):
    resume_count: int
    interview_sessions: int
    roadmaps: int
    quizzes_taken: int
    skill_evaluations: int = 0
    overall_completion_percent: int


class ProgressScores(BaseModel):
    average_interview_score: float
    average_quiz_percent: float
    average_skill_score: float = 0.0


class ProgressDashboardResponse(BaseModel):
    summary: ProgressSummary
    scores: ProgressScores
    updated_at: datetime | str
