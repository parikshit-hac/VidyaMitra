import re
from datetime import datetime
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.interview import Interview
from app.services.grok_service import generate_json
from app.utils.dynamic_engine import infer_role_cluster


def _dynamic_questions_with_grok(role: str, experience_level: str, focus_areas: list[str]) -> list[dict[str, str]]:
    prompt = (
        "Create interview questions JSON for a job role.\n"
        f"role={role}\nexperience_level={experience_level}\nfocus_areas={focus_areas}\n"
        'Return object: {"questions":[{"question":"...","competency":"..."}]} with 6 diverse questions.'
    )
    data = generate_json(prompt)
    raw_questions = data.get("questions", [])
    questions: list[dict[str, str]] = []
    if isinstance(raw_questions, list):
        for item in raw_questions:
            if not isinstance(item, dict):
                continue
            question = str(item.get("question", "")).strip()
            competency = str(item.get("competency", "General")).strip() or "General"
            if question:
                questions.append({"question": question, "competency": competency})
    return questions[:6]


def generate_mock_questions(role: str, experience_level: str = "beginner", focus_areas: list[str] | None = None) -> list[dict[str, str]]:
    focus_areas = focus_areas or []
    dynamic = _dynamic_questions_with_grok(role=role, experience_level=experience_level, focus_areas=focus_areas)
    if len(dynamic) < 4:
        raise HTTPException(status_code=502, detail="Interview question generation returned insufficient questions.")
    return dynamic


def _tokenize(text: str) -> set[str]:
    return set(re.findall(r"[a-zA-Z]{3,}", text.lower()))


def _score_tone(answer: str) -> int:
    positive = ["learned", "improved", "collaborated", "resolved", "delivered", "owned", "supported"]
    negative = ["can't", "never", "hate", "stupid", "impossible", "useless"]
    lowered = answer.lower()
    pos_hits = sum(1 for w in positive if w in lowered)
    neg_hits = sum(1 for w in negative if w in lowered)
    score = 65 + (pos_hits * 6) - (neg_hits * 10)
    return max(30, min(95, score))


def _score_confidence(answer: str) -> int:
    confident = ["i led", "i built", "i improved", "i delivered", "i implemented", "i analyzed"]
    weak = ["maybe", "i think", "probably", "sort of", "kind of", "not sure"]
    lowered = answer.lower()
    conf_hits = sum(1 for w in confident if w in lowered)
    weak_hits = sum(1 for w in weak if w in lowered)
    length_bonus = 10 if len(answer.split()) >= 70 else 0
    score = 60 + conf_hits * 7 - weak_hits * 8 + length_bonus
    return max(25, min(98, score))


def _score_accuracy(question: str, answer: str) -> int:
    q = _tokenize(question)
    a = _tokenize(answer)
    if not q:
        return 60
    overlap = len(q & a)
    ratio = overlap / max(1, len(q))
    length_factor = min(1.0, len(answer.split()) / 100)
    score = int(35 + (ratio * 45) + (length_factor * 20))
    return max(20, min(97, score))


def _build_feedback(role: str, question: str, answer: str, target_role: str = "", competency: str = "General") -> dict:
    tone_score = _score_tone(answer)
    confidence_score = _score_confidence(answer)
    accuracy_score = _score_accuracy(question, answer)
    overall = int((tone_score * 0.25) + (confidence_score * 0.35) + (accuracy_score * 0.40))

    strengths: list[str] = []
    improvements: list[str] = []

    if tone_score >= 75:
        strengths.append("Professional and constructive communication tone.")
    else:
        improvements.append("Use more positive and solution-oriented wording.")

    if confidence_score >= 75:
        strengths.append("Confident ownership shown with first-person action statements.")
    else:
        improvements.append("Use clear ownership phrases like 'I implemented' and reduce hedging words.")

    if accuracy_score >= 75:
        strengths.append(f"Response stays close to the question and the {competency.lower()} competency.")
    else:
        improvements.append("Address the exact question first, then add examples and impact metrics.")

    personalized_guidance = [
        f"For {target_role or role}, structure answers as Situation -> Action -> Result.",
        "Quantify outcomes where possible (time saved, growth %, accuracy lift).",
        f"Close by linking your example back to {competency.lower()} and business impact.",
    ]

    return {
        "question": question,
        "competency": competency,
        "overall_score": overall,
        "tone_score": tone_score,
        "confidence_score": confidence_score,
        "accuracy_score": accuracy_score,
        "strengths": strengths,
        "improvements": improvements,
        "personalized_guidance": personalized_guidance,
    }


def _serialize_session(session: Interview) -> dict:
    meta = session.meta or {}
    questions = meta.get("questions", [])
    answers = meta.get("answers", [])
    return {
        "session_id": str(session.id),
        "role": session.role or "Unknown",
        "experience_level": str(meta.get("experience_level") or "beginner"),
        "focus_areas": [str(area) for area in meta.get("focus_areas", []) if str(area).strip()],
        "questions": questions,
        "current_question_index": min(len(answers), len(questions) - 1) if questions else 0,
        "answered_count": len(answers),
        "total_questions": len(questions),
        "status": session.status or "in_progress",
        "created_at": session.created_at,
    }


def start_mock_interview_session(
    db: Session,
    user_id: UUID,
    role: str,
    experience_level: str = "beginner",
    focus_areas: list[str] | None = None,
) -> dict:
    questions = generate_mock_questions(role=role, experience_level=experience_level, focus_areas=focus_areas)
    session = Interview(
        user_id=user_id,
        company="Mock Interview",
        role=role,
        mode="online",
        status="in_progress",
        notes="Dynamic AI mock interview session",
        meta={
            "type": "mock_interview_session",
            "experience_level": experience_level,
            "focus_areas": focus_areas or [],
            "questions": questions,
            "answers": [],
            "feedback_history": [],
            "overall_score": 0,
            "role_cluster": infer_role_cluster(role),
        },
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return _serialize_session(session)


def get_mock_interview_session(db: Session, user_id: UUID, session_id: str) -> dict:
    session = (
        db.query(Interview)
        .filter(Interview.id == session_id, Interview.user_id == user_id)
        .first()
    )
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found.")
    return _serialize_session(session)


def submit_mock_interview_answer(
    db: Session,
    user_id: UUID,
    session_id: str,
    answer: str,
    question_index: int,
    target_role: str = "",
) -> dict:
    session = (
        db.query(Interview)
        .filter(Interview.id == session_id, Interview.user_id == user_id)
        .first()
    )
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found.")

    meta = dict(session.meta or {})
    questions = meta.get("questions", [])
    answers = list(meta.get("answers", []))
    feedback_history = list(meta.get("feedback_history", []))

    if not questions:
        raise HTTPException(status_code=400, detail="Interview session has no generated questions.")
    if question_index < 0 or question_index >= len(questions):
        raise HTTPException(status_code=400, detail="Invalid question index for this interview session.")

    question_data = questions[question_index]
    question = str(question_data.get("question", "")).strip()
    competency = str(question_data.get("competency", "General")).strip() or "General"
    if not question:
        raise HTTPException(status_code=400, detail="Selected interview question is invalid.")

    feedback = _build_feedback(
        role=session.role or "Unknown",
        question=question,
        answer=answer,
        target_role=target_role,
        competency=competency,
    )

    answer_entry = {
        "question_index": question_index,
        "question": question,
        "competency": competency,
        "answer": answer,
        "feedback": feedback,
        "submitted_at": datetime.utcnow().isoformat(),
    }

    replaced = False
    for idx, existing in enumerate(answers):
        if int(existing.get("question_index", -1)) == question_index:
            answers[idx] = answer_entry
            replaced = True
            break
    if not replaced:
        answers.append(answer_entry)
        answers.sort(key=lambda item: int(item.get("question_index", 0)))

    feedback_history = [item for item in feedback_history if int(item.get("question_index", -1)) != question_index]
    feedback_history.append({"question_index": question_index, **feedback})
    feedback_history.sort(key=lambda item: int(item.get("question_index", 0)))

    scores = [int(item.get("feedback", {}).get("overall_score", 0)) for item in answers]
    overall_score = int(sum(scores) / len(scores)) if scores else int(feedback["overall_score"])
    answered_count = len(answers)
    status = "completed" if answered_count >= len(questions) else "in_progress"

    meta["answers"] = answers
    meta["feedback_history"] = feedback_history
    meta["feedback"] = feedback
    meta["overall_score"] = overall_score
    session.meta = meta
    session.status = status
    db.add(session)
    db.commit()
    db.refresh(session)

    return {
        "session_id": str(session.id),
        "role": session.role or "Unknown",
        "question": question,
        "competency": competency,
        "question_index": question_index,
        "answered_count": answered_count,
        "total_questions": len(questions),
        "status": status,
        "overall_score": feedback["overall_score"],
        "tone_score": feedback["tone_score"],
        "confidence_score": feedback["confidence_score"],
        "accuracy_score": feedback["accuracy_score"],
        "strengths": feedback["strengths"],
        "improvements": feedback["improvements"],
        "personalized_guidance": feedback["personalized_guidance"],
        "created_at": session.created_at,
    }


def evaluate_mock_interview(db: Session, user_id: UUID, role: str, question: str, answer: str, target_role: str = "") -> dict:
    feedback = _build_feedback(role=role, question=question, answer=answer, target_role=target_role)
    session = Interview(
        user_id=user_id,
        company="Mock Interview",
        role=role,
        mode="online",
        status="completed",
        notes="AI-evaluated mock interview response",
        meta={
            "type": "single_mock_answer",
            "feedback": feedback,
            "overall_score": feedback["overall_score"],
            "role_cluster": infer_role_cluster(role),
            "questions": [{"question": question, "competency": feedback["competency"]}],
            "answers": [{"question_index": 0, "question": question, "answer": answer, "feedback": feedback}],
            "feedback_history": [{"question_index": 0, **feedback}],
        },
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    return {
        "session_id": str(session.id),
        "role": session.role or role,
        "question": question,
        "competency": feedback["competency"],
        "question_index": 0,
        "answered_count": 1,
        "total_questions": 1,
        "status": "completed",
        "overall_score": feedback["overall_score"],
        "tone_score": feedback["tone_score"],
        "confidence_score": feedback["confidence_score"],
        "accuracy_score": feedback["accuracy_score"],
        "strengths": feedback["strengths"],
        "improvements": feedback["improvements"],
        "personalized_guidance": feedback["personalized_guidance"],
        "created_at": session.created_at,
    }


def list_interview_sessions(db: Session, user_id: UUID, limit: int = 20) -> list[dict]:
    rows = (
        db.query(Interview)
        .filter(Interview.user_id == user_id)
        .order_by(Interview.created_at.desc())
        .limit(max(1, min(limit, 100)))
        .all()
    )
    result: list[dict] = []
    for row in rows:
        meta = row.meta or {}
        feedback = meta.get("feedback", {})
        questions = meta.get("questions", [])
        answers = meta.get("answers", [])
        result.append(
            {
                "id": str(row.id),
                "role": row.role or "Unknown",
                "score": int(meta.get("overall_score") or 0),
                "created_at": row.created_at or datetime.utcnow(),
                "status": row.status or "completed",
                "answered_count": len(answers),
                "total_questions": len(questions),
                "feedback": feedback,
            }
        )
    return result
