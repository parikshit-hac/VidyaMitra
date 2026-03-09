from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.interview_schema import (
    InterviewSessionResponse,
    MockInterviewEvaluateRequest,
    MockInterviewFeedbackResponse,
    MockInterviewQuestionsResponse,
    MockInterviewRequest,
    MockInterviewSessionAnswerRequest,
    MockInterviewSessionResponse,
)
from app.services.interview_service import (
    evaluate_mock_interview,
    generate_mock_questions,
    get_mock_interview_session,
    list_interview_sessions,
    start_mock_interview_session,
    submit_mock_interview_answer,
)


router = APIRouter(prefix="/interview", tags=["Interview"])


@router.get("/health")
def interview_health(_: User = Depends(get_current_user)) -> dict[str, str]:
    return {"message": "Interview router ready"}


@router.post("/mock/questions", response_model=MockInterviewQuestionsResponse)
def mock_questions(payload: MockInterviewRequest, _: User = Depends(get_current_user)) -> MockInterviewQuestionsResponse:
    questions = generate_mock_questions(
        role=payload.role,
        experience_level=payload.experience_level,
        focus_areas=payload.focus_areas,
    )
    return MockInterviewQuestionsResponse(role=payload.role, questions=questions)


@router.post("/mock/session", response_model=MockInterviewSessionResponse)
def create_mock_session(
    payload: MockInterviewRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MockInterviewSessionResponse:
    result = start_mock_interview_session(
        db=db,
        user_id=user.id,
        role=payload.role,
        experience_level=payload.experience_level,
        focus_areas=payload.focus_areas,
    )
    return MockInterviewSessionResponse(**result)


@router.get("/mock/session/{session_id}", response_model=MockInterviewSessionResponse)
def read_mock_session(
    session_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MockInterviewSessionResponse:
    result = get_mock_interview_session(db=db, user_id=user.id, session_id=session_id)
    return MockInterviewSessionResponse(**result)


@router.post("/mock/session/{session_id}/answer", response_model=MockInterviewFeedbackResponse)
def answer_mock_session_question(
    session_id: str,
    payload: MockInterviewSessionAnswerRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MockInterviewFeedbackResponse:
    result = submit_mock_interview_answer(
        db=db,
        user_id=user.id,
        session_id=session_id,
        answer=payload.answer,
        question_index=payload.question_index,
        target_role=payload.target_role,
    )
    return MockInterviewFeedbackResponse(**result)


@router.post("/mock/evaluate", response_model=MockInterviewFeedbackResponse)
def mock_evaluate(
    payload: MockInterviewEvaluateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MockInterviewFeedbackResponse:
    result = evaluate_mock_interview(
        db=db,
        user_id=user.id,
        role=payload.role,
        question=payload.question,
        answer=payload.answer,
        target_role=payload.target_role,
    )
    return MockInterviewFeedbackResponse(**result)


@router.get("/sessions", response_model=list[InterviewSessionResponse])
def interview_sessions(
    limit: int = 20,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[InterviewSessionResponse]:
    rows = list_interview_sessions(db=db, user_id=user.id, limit=limit)
    return [InterviewSessionResponse(**row) for row in rows]
