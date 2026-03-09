from app.services.career_service import generate_roadmap


def run(goal: str, target_role: str = "", constraints: str = "") -> dict:
    data = generate_roadmap(
        goal=goal,
        background="Orchestrator mode",
        target_role=target_role,
        constraints=constraints,
    )
    return {
        "summary": data.get("ai_guidance", ""),
        "roadmap": data.get("langchain_roadmap", ""),
        "sources": {
            "ai": data.get("ai_source"),
            "agent": data.get("agent_source"),
        },
    }
