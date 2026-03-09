from datetime import datetime

from pydantic import BaseModel, Field


class InterviewSummary(BaseModel):
    id: str
    role: str
    score: int


class MockInterviewRequest(BaseModel):
    role: str = Field(min_length=2, max_length=120)
    experience_level: str = Field(default="beginner", max_length=50)
    focus_areas: list[str] = Field(default_factory=list)
    difficulty: str = Field(default="medium", max_length=20)


class MockInterviewQuestion(BaseModel):
    question: str
    competency: str


class MockInterviewQuestionsResponse(BaseModel):
    role: str
    questions: list[MockInterviewQuestion]


class MockInterviewSessionResponse(BaseModel):
    session_id: str
    role: str
    experience_level: str
    focus_areas: list[str]
    questions: list[MockInterviewQuestion]
    current_question_index: int
    answered_count: int
    total_questions: int
    status: str
    created_at: datetime | None = None


class MockInterviewSessionAnswerRequest(BaseModel):
    answer: str = Field(min_length=10, max_length=5000)
    question_index: int = Field(ge=0, default=0)
    target_role: str = Field(default="", max_length=120)


class MockInterviewEvaluateRequest(BaseModel):
    role: str = Field(min_length=2, max_length=120)
    question: str = Field(min_length=5, max_length=1000)
    answer: str = Field(min_length=10, max_length=5000)
    target_role: str = Field(default="", max_length=120)


class MockInterviewFeedbackResponse(BaseModel):
    session_id: str
    role: str
    question: str | None = None
    competency: str | None = None
    question_index: int | None = None
    answered_count: int | None = None
    total_questions: int | None = None
    status: str | None = None
    overall_score: int
    tone_score: int
    confidence_score: int
    accuracy_score: int
    strengths: list[str]
    improvements: list[str]
    personalized_guidance: list[str]
    created_at: datetime | None = None


class InterviewSessionResponse(BaseModel):
    id: str
    role: str
    score: int
    created_at: datetime
    status: str
    answered_count: int
    total_questions: int
    feedback: dict
