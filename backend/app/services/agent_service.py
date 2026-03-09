from fastapi import HTTPException

from app.services.grok_service import generate_career_support


def run_career_agent(goal: str, background: str = "", target_role: str = "", constraints: str = "") -> str:
    prompt = (
        "You are VidyaMitra career agent.\n"
        "Return a practical 8-week roadmap with milestones, tools, and weekly actions.\n"
        f"Goal: {goal}\n"
        f"Background: {background}\n"
        f"Target role: {target_role}\n"
        f"Constraints: {constraints}"
    )
    try:
        return generate_career_support(prompt)
    except HTTPException:
        raise
