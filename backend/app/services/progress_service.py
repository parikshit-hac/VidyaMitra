from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.interview import Interview
from app.models.learning_plan import LearningPlan
from app.models.quiz import Quiz
from app.models.resume import Resume
from app.models.skill_evaluation import SkillEvaluation
from app.models.user_progress import UserProgress


def get_progress_dashboard(db: Session, user_id: UUID) -> dict:
    resume_count = db.query(Resume).filter(Resume.user_id == user_id).count()
    interview_rows = db.query(Interview).filter(Interview.user_id == user_id).all()
    interview_count = len(interview_rows)
    roadmap_count = db.query(LearningPlan).filter(LearningPlan.user_id == user_id).count()
    quiz_rows = db.query(Quiz).filter(Quiz.user_id == user_id).all()
    skill_rows = db.query(SkillEvaluation).filter(SkillEvaluation.user_id == user_id).all()

    interview_scores: list[float] = []
    for interview in interview_rows:
        meta = interview.meta or {}
        try:
            interview_scores.append(float(meta.get("overall_score") or 0.0))
        except (TypeError, ValueError):
            continue
    avg_interview_score = (sum(interview_scores) / len(interview_scores)) if interview_scores else 0.0
    avg_quiz_pct = 0.0
    if quiz_rows:
        pcts = []
        for q in quiz_rows:
            max_score = float(q.max_score or 0)
            score = float(q.score or 0)
            pcts.append((score / max_score) * 100 if max_score else 0.0)
        avg_quiz_pct = sum(pcts) / len(pcts)
    avg_skill_score = 0.0
    if skill_rows:
        values = [float(row.score or 0.0) for row in skill_rows]
        avg_skill_score = sum(values) / len(values)

    completion = min(
        100,
        int(
            (15 if resume_count > 0 else 0)
            + (25 if interview_count >= 2 else interview_count * 10)
            + (30 if roadmap_count > 0 else 0)
            + (30 if len(quiz_rows) >= 2 else len(quiz_rows) * 10)
        ),
    )

    dashboard = {
        "summary": {
            "resume_count": resume_count,
            "interview_sessions": interview_count,
            "roadmaps": roadmap_count,
            "quizzes_taken": len(quiz_rows),
            "skill_evaluations": len(skill_rows),
            "overall_completion_percent": completion,
        },
        "scores": {
            "average_interview_score": round(float(avg_interview_score), 2),
            "average_quiz_percent": round(float(avg_quiz_pct), 2),
            "average_skill_score": round(float(avg_skill_score), 2),
        },
        "updated_at": datetime.utcnow().isoformat(),
    }
    return dashboard


def sync_progress(db: Session, user_id: UUID) -> dict:
    dashboard = get_progress_dashboard(db, user_id)
    row = db.query(UserProgress).filter(UserProgress.user_id == user_id).first()
    if row:
        row.progress = dashboard
        row.updated_at = datetime.utcnow()
    else:
        row = UserProgress(user_id=user_id, progress=dashboard, updated_at=datetime.utcnow())
        db.add(row)
    db.commit()
    db.refresh(row)
    return {"progress_id": str(row.id), "progress": row.progress, "updated_at": row.updated_at}
