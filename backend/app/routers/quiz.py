from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.quiz_schema import (
    QuizGenerateRequest,
    QuizGenerateResponse,
    QuizHistoryItem,
    QuizSubmitRequest,
    QuizSubmitResponse,
)
from app.services.quiz_service import generate_quiz, list_quiz_history, submit_quiz


router = APIRouter(prefix="/quiz", tags=["Quiz"])


@router.post("/generate", response_model=QuizGenerateResponse)
def quiz_generate(payload: QuizGenerateRequest, _: User = Depends(get_current_user)) -> QuizGenerateResponse:
    data = generate_quiz(topic=payload.topic, level=payload.level, num_questions=payload.num_questions)
    return QuizGenerateResponse(**data)


@router.post("/submit", response_model=QuizSubmitResponse)
def quiz_submit(
    payload: QuizSubmitRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> QuizSubmitResponse:
    data = submit_quiz(
        db=db,
        user_id=user.id,
        topic=payload.topic,
        level=payload.level,
        questions=[q.model_dump() for q in payload.questions],
        user_answers=payload.user_answers,
    )
    return QuizSubmitResponse(**data)


@router.get("/history", response_model=list[QuizHistoryItem])
def quiz_history(
    limit: int = 20,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[QuizHistoryItem]:
    rows = list_quiz_history(db=db, user_id=user.id, limit=limit)
    return [QuizHistoryItem(**row) for row in rows]
