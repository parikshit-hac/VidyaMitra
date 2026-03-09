from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class QuizGenerateRequest(BaseModel):
    topic: str = Field(min_length=2, max_length=120)
    level: str = Field(default="beginner", max_length=30)
    num_questions: int = Field(default=5, ge=3, le=10)


class QuizQuestion(BaseModel):
    id: int
    question: str
    options: list[str]
    correct_option: int
    explanation: str


class QuizGenerateResponse(BaseModel):
    topic: str
    level: str
    questions: list[QuizQuestion]


class QuizSubmitRequest(BaseModel):
    topic: str = Field(min_length=2, max_length=120)
    level: str = Field(default="beginner", max_length=30)
    questions: list[QuizQuestion]
    user_answers: list[int]


class QuizSubmitResponse(BaseModel):
    quiz_id: UUID
    topic: str
    score: float
    max_score: float
    percentage: float
    feedback: list[str]
    created_at: datetime | None = None


class QuizHistoryItem(BaseModel):
    id: UUID
    title: str | None = None
    score: float | None = None
    max_score: float | None = None
    percentage: float
    taken_at: datetime | None = None
