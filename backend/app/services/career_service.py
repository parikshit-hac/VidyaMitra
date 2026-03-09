from datetime import datetime
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.learning_plan import LearningPlan
from app.services.agent_service import run_career_agent
from app.services.grok_service import generate_career_support, generate_json
from app.utils.dynamic_engine import extract_skills_from_text, required_skills_for_role, skill_gaps as compute_skill_gaps


def generate_roadmap(goal: str, background: str = "", target_role: str = "", constraints: str = "") -> dict:
    prompt = (
        "Create a personalized career support response.\n"
        f"Goal: {goal}\n"
        f"Background: {background}\n"
        f"Target role: {target_role}\n"
        f"Constraints: {constraints}"
    )
    ai_response = generate_career_support(prompt)
    ai_source = "groq"
    agent_response = run_career_agent(goal, background, target_role, constraints)
    agent_source = "groq-agent"
    return {
        "goal": goal,
        "ai_guidance": ai_response,
        "ai_source": ai_source,
        "agent_source": agent_source,
        "langchain_roadmap": agent_response,
    }


def _normalize_skills(skills: list[str]) -> set[str]:
    return {s.strip().lower() for s in skills if s and s.strip()}


def _clean_string_list(items: list, limit: int) -> list[str]:
    return [str(item).strip() for item in items if str(item).strip()][:limit]


def _clean_learning_path(raw_path: list, limit: int) -> list[dict]:
    cleaned: list[dict] = []
    for item in raw_path[:limit]:
        if not isinstance(item, dict):
            continue
        phase = str(item.get("phase", "")).strip()
        topics = _clean_string_list(item.get("topics", []), 6) if isinstance(item.get("topics", []), list) else []
        outcome = str(item.get("outcome", "")).strip()
        if phase and topics:
            cleaned.append({"phase": phase, "topics": topics, "outcome": outcome})
    return cleaned


def _clean_weekly_plan(raw_plan: list, timeline_weeks: int, available_hours_per_week: int) -> list[dict]:
    cleaned: list[dict] = []
    for index, item in enumerate(raw_plan[:timeline_weeks], start=1):
        if not isinstance(item, dict):
            continue
        focus = str(item.get("focus", "")).strip()
        deliverable = str(item.get("deliverable", "")).strip()
        try:
            hours = int(item.get("hours", available_hours_per_week))
        except (TypeError, ValueError):
            hours = available_hours_per_week
        if focus:
            cleaned.append(
                {
                    "week": index,
                    "focus": focus,
                    "hours": max(1, min(hours, available_hours_per_week)),
                    "deliverable": deliverable,
                }
            )
    return cleaned


def build_transition_plan(
    db: Session,
    user_id: UUID,
    target_role: str,
    current_skills: list[str],
    experience_summary: str = "",
    resume_summary: str = "",
    available_hours_per_week: int = 8,
    timeline_weeks: int = 12,
) -> dict:
    context_text = f"{experience_summary}\n{resume_summary}\n{', '.join(current_skills)}"
    target_skills = required_skills_for_role(target_role, context_text=context_text)
    normalized_current = _normalize_skills(current_skills)
    inferred_from_text = extract_skills_from_text(f"{experience_summary} {resume_summary}", target_skills)
    current_union = sorted(set([*current_skills, *list(normalized_current), *inferred_from_text]))
    skill_gaps = compute_skill_gaps(current_union, target_skills)
    dynamic = generate_json(
        "Build dynamic career transition roadmap JSON.\n"
        f"target_role={target_role}\ncurrent_skills={current_union}\ntarget_skills={target_skills}\nskill_gaps={skill_gaps}\n"
        f"experience_summary={experience_summary}\nresume_summary={resume_summary}\n"
        f"timeline_weeks={timeline_weeks}\navailable_hours_per_week={available_hours_per_week}\n"
        'Return {"transferable_strengths":[...], "skill_gaps":[...], "recommended_certifications":[...], '
        '"learning_path":[{"phase":"...","topics":[...],"outcome":"..."}], '
        '"weekly_plan":[{"week":1,"focus":"...","hours":8,"deliverable":"..."}], "notes":"..."}'
    )
    strengths = dynamic.get("transferable_strengths")
    dynamic_skill_gaps = dynamic.get("skill_gaps")
    certs = dynamic.get("recommended_certifications")
    path = dynamic.get("learning_path")
    plan = dynamic.get("weekly_plan")
    notes = str(dynamic.get("notes", "")).strip()
    if not isinstance(strengths, list) or not strengths:
        raise HTTPException(status_code=502, detail="Career roadmap response missing transferable strengths.")
    if not isinstance(dynamic_skill_gaps, list) or not dynamic_skill_gaps:
        raise HTTPException(status_code=502, detail="Career roadmap response missing skill gaps.")
    if not isinstance(certs, list) or not certs:
        raise HTTPException(status_code=502, detail="Career roadmap response missing certifications.")
    if not isinstance(path, list) or not path:
        raise HTTPException(status_code=502, detail="Career roadmap response missing learning path.")
    if not isinstance(plan, list) or not plan:
        raise HTTPException(status_code=502, detail="Career roadmap response missing weekly plan.")
    if not notes:
        raise HTTPException(status_code=502, detail="Career roadmap response missing notes.")

    transferable_strengths = _clean_string_list(strengths, 8)
    normalized_dynamic_gaps = _clean_string_list(dynamic_skill_gaps, 10)
    recommended_certifications = _clean_string_list(certs, 8)
    learning_path = _clean_learning_path(path, 6)
    weekly_plan = _clean_weekly_plan(plan, timeline_weeks, available_hours_per_week)

    if not transferable_strengths:
        raise HTTPException(status_code=502, detail="Career roadmap response returned empty transferable strengths.")
    if not normalized_dynamic_gaps:
        raise HTTPException(status_code=502, detail="Career roadmap response returned empty skill gaps.")
    if not recommended_certifications:
        raise HTTPException(status_code=502, detail="Career roadmap response returned empty certifications.")
    if not learning_path:
        raise HTTPException(status_code=502, detail="Career roadmap response returned empty learning path.")
    if not weekly_plan:
        raise HTTPException(status_code=502, detail="Career roadmap response returned empty weekly plan.")

    milestones = {
        "target_role": target_role,
        "transferable_strengths": transferable_strengths,
        "skill_gaps": normalized_dynamic_gaps,
        "required_skills": target_skills,
        "current_skills": current_union,
        "recommended_certifications": recommended_certifications,
        "learning_path": learning_path,
        "weekly_plan": weekly_plan,
        "notes": notes,
    }

    row = LearningPlan(
        user_id=user_id,
        title=f"{target_role} transition plan",
        goals=[target_role],
        status="active",
        meta=milestones,
    )
    db.add(row)
    db.commit()
    db.refresh(row)

    return {
        "roadmap_id": str(row.id),
        "target_role": target_role,
        "transferable_strengths": transferable_strengths,
        "skill_gaps": normalized_dynamic_gaps,
        "recommended_certifications": recommended_certifications,
        "learning_path": learning_path,
        "weekly_plan": weekly_plan,
        "notes": notes,
        "created_at": row.created_at or datetime.utcnow(),
    }


def list_transition_plans(db: Session, user_id: UUID, limit: int = 20) -> list[dict]:
    rows = (
        db.query(LearningPlan)
        .filter(LearningPlan.user_id == user_id)
        .order_by(LearningPlan.created_at.desc())
        .limit(max(1, min(limit, 100)))
        .all()
    )
    output: list[dict] = []
    for row in rows:
        milestones = row.meta or {}

        output.append(
            {
                "id": str(row.id),
                "goal": (row.goals or [row.title or "Career Plan"])[0],
                "milestones": milestones,
                "created_at": row.created_at or datetime.utcnow(),
            }
        )
    return output
