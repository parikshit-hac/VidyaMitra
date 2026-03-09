from uuid import UUID

from sqlalchemy.orm import Session

from app.services.resume_service import list_resumes


def run(db: Session, user_id: UUID, target_role: str = "") -> dict:
    resumes = list_resumes(db=db, user_id=user_id, limit=5)
    latest = resumes[0] if resumes else None
    return {
        "latest_resume": latest,
        "resume_count": len(resumes),
        "target_role_hint": target_role,
        "next_action": "Upload or re-analyze resume for role alignment" if not latest else "Review latest resume analysis",
    }
