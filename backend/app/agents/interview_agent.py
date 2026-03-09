from uuid import UUID

from sqlalchemy.orm import Session

from app.services.interview_service import generate_mock_questions, list_interview_sessions


def run(db: Session, user_id: UUID, target_role: str = "") -> dict:
    sessions = list_interview_sessions(db=db, user_id=user_id, limit=5)
    questions = generate_mock_questions(role=target_role or "general", experience_level="intermediate", focus_areas=[])
    avg_score = round(sum(int(s.get("score", 0)) for s in sessions) / len(sessions), 2) if sessions else 0
    return {
        "recent_session_count": len(sessions),
        "average_score": avg_score,
        "next_questions": questions[:3],
        "next_action": "Practice one mock interview and improve lowest scoring competency",
    }
