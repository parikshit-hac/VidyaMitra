from datetime import datetime
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.quiz import Quiz
from app.services.grok_service import generate_json


def generate_quiz(topic: str, level: str, num_questions: int) -> dict:
    num_questions = max(3, min(num_questions, 15))
    data = generate_json(
        "Create role-specific MCQ quiz.\n"
        f"topic={topic}\nlevel={level}\nnum_questions={num_questions}\n"
        'Return {"questions":[{"question":"...","options":["a","b","c","d"],"correct_option":0,"explanation":"...","skill":"..."}]}'
    )
    raw_questions = data.get("questions", [])
    if not isinstance(raw_questions, list) or not raw_questions:
        raise HTTPException(status_code=502, detail="Grok quiz response missing questions.")

    questions = []
    for idx, item in enumerate(raw_questions[:num_questions], start=1):
        if not isinstance(item, dict):
            continue
        options = item.get("options", [])
        if not isinstance(options, list) or len(options) < 2:
            continue
        questions.append(
            {
                "id": idx,
                "question": str(item.get("question", "")).strip(),
                "options": [str(opt) for opt in options][:4],
                "correct_option": int(item.get("correct_option", 0)),
                "explanation": str(item.get("explanation", "")).strip(),
                "skill": str(item.get("skill", "general")).strip() or "general",
            }
        )
    if len(questions) < min(3, num_questions):
        raise HTTPException(status_code=502, detail="Grok quiz response returned insufficient valid questions.")
    return {"topic": topic, "level": level, "questions": questions}


def submit_quiz(
    db: Session,
    user_id: UUID,
    topic: str,
    level: str,
    questions: list[dict],
    user_answers: list[int],
) -> dict:
    max_score = float(len(questions))
    score = 0.0
    feedback: list[str] = []

    for idx, q in enumerate(questions):
        correct = int(q.get("correct_option", -1))
        options = q.get("options", [])
        max_idx = len(options) - 1 if isinstance(options, list) else 3
        correct = min(max(correct, 0), max(0, max_idx))
        answer = user_answers[idx] if idx < len(user_answers) else -1
        if answer == correct:
            score += 1.0
        else:
            feedback.append(
                f"Q{idx + 1}: {q.get('question', 'Question')} | Correct option: {correct + 1}. {q.get('explanation', '')}"
            )

    percentage = round((score / max_score) * 100, 2) if max_score else 0.0

    details = {
        "topic": topic,
        "level": level,
        "questions": questions,
        "user_answers": user_answers,
        "feedback": feedback[:5],
    }
    row = Quiz(
        user_id=user_id,
        title=f"{topic} quiz",
        score=score,
        max_score=max_score,
        details=details,
        taken_at=datetime.utcnow(),
    )
    db.add(row)
    db.commit()
    db.refresh(row)

    return {
        "quiz_id": row.id,
        "topic": topic,
        "score": float(score),
        "max_score": float(max_score),
        "percentage": percentage,
        "feedback": feedback[:5] if feedback else ["Strong performance. Keep practicing scenario-based questions."],
        "created_at": row.created_at,
    }


def list_quiz_history(db: Session, user_id: UUID, limit: int = 20) -> list[dict]:
    rows = (
        db.query(Quiz)
        .filter(Quiz.user_id == user_id)
        .order_by(Quiz.created_at.desc())
        .limit(max(1, min(limit, 100)))
        .all()
    )
    out: list[dict] = []
    for row in rows:
        max_score = float(row.max_score or 0)
        score = float(row.score or 0)
        pct = round((score / max_score) * 100, 2) if max_score else 0.0
        out.append(
            {
                "id": row.id,
                "title": row.title,
                "score": score,
                "max_score": max_score,
                "percentage": pct,
                "taken_at": row.taken_at or row.created_at,
            }
        )
    return out
