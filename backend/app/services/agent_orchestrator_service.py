from datetime import datetime
import json
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.agents import career_agent, interview_agent, resource_agent, resume_agent
from app.models.agent_run import AgentRun
from app.services.grok_service import generate_json
from app.services.progress_service import get_progress_dashboard
from app.utils.dynamic_engine import infer_role_cluster


def _json_safe(value):
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): _json_safe(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_json_safe(v) for v in value]
    if isinstance(value, tuple):
        return [_json_safe(v) for v in value]
    return value


def _compact_for_prompt(value, depth: int = 0):
    if depth > 3:
        return None
    if isinstance(value, dict):
        items = list(value.items())[:10]
        compacted = {}
        for k, v in items:
            compacted[str(k)] = _compact_for_prompt(v, depth + 1)
        return compacted
    if isinstance(value, list):
        return [_compact_for_prompt(v, depth + 1) for v in value[:6]]
    if isinstance(value, tuple):
        return [_compact_for_prompt(v, depth + 1) for v in value[:6]]
    if isinstance(value, str):
        text = value.strip()
        return text[:240] + ("..." if len(text) > 240 else "")
    return value


def _compact_json_text(value, max_chars: int = 2200) -> str:
    compacted = _compact_for_prompt(value)
    text = json.dumps(compacted, separators=(",", ":"), ensure_ascii=True)
    if len(text) > max_chars:
        return text[:max_chars] + "..."
    return text


def _build_plan(goal: str, target_role: str, include_resources: bool, include_progress: bool) -> list[dict]:
    inferred = infer_role_cluster(target_role or goal)
    plan = [
        {"agent": "resume_agent", "action": "review_resume_context", "requires_approval": False},
        {"agent": "career_agent", "action": "generate_role_roadmap", "requires_approval": False},
        {"agent": "interview_agent", "action": "prepare_mock_interview_path", "requires_approval": False},
    ]
    if include_resources:
        plan.append({"agent": "resource_agent", "action": "fetch_learning_and_market_resources", "requires_approval": False})
    if include_progress:
        plan.append({"agent": "progress_agent", "action": "summarize_progress_state", "requires_approval": False})

    plan.append(
        {
            "agent": "orchestrator",
            "action": f"synthesize_final_plan_for_{inferred.replace(' ', '_')}",
            "requires_approval": False,
        }
    )
    return plan


def _execute_step(
    db: Session,
    user_id: UUID,
    step: dict,
    goal: str,
    target_role: str,
    constraints: str,
) -> dict:
    agent = step["agent"]
    action = step["action"]

    if agent == "resume_agent":
        output = resume_agent.run(db=db, user_id=user_id, target_role=target_role)
    elif agent == "career_agent":
        output = career_agent.run(goal=goal, target_role=target_role, constraints=constraints)
    elif agent == "interview_agent":
        output = interview_agent.run(db=db, user_id=user_id, target_role=target_role)
    elif agent == "resource_agent":
        output = resource_agent.run(topic=target_role or goal)
    elif agent == "progress_agent":
        output = get_progress_dashboard(db=db, user_id=user_id)
    else:
        output = {"message": f"Completed action: {action}"}

    return {
        "agent": agent,
        "action": action,
        "status": "completed",
        "needs_approval": bool(step.get("requires_approval", False)),
        "output": output,
    }


def _label_trace_actions(trace: list[dict], goal: str, target_role: str, constraints: str) -> list[dict]:
    trace_summary = [
        {
            "step_id": step.get("step_id"),
            "agent": step.get("agent"),
            "action_key": step.get("action"),
            "status": step.get("status"),
            "output": _compact_for_prompt(step.get("output", {})),
        }
        for step in trace
    ]
    prompt = (
        "Rewrite technical agent step actions into user-friendly, dynamic labels.\n"
        f"goal={goal}\n"
        f"target_role={target_role}\n"
        f"constraints={constraints}\n"
        f"trace={_compact_json_text(trace_summary, max_chars=2600)}\n"
        'Return JSON object: {"steps":[{"step_id":1,"action_label":"..."}]}. '
        "Each action_label must be specific to that step output and context."
    )
    data = generate_json(prompt)
    raw_steps = data.get("steps", [])
    if not isinstance(raw_steps, list) or not raw_steps:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Orchestrator AI labeling returned invalid steps payload.",
        )
    label_map: dict[int, str] = {}
    for item in raw_steps:
        if not isinstance(item, dict):
            continue
        try:
            step_id = int(item.get("step_id"))
        except (TypeError, ValueError):
            continue
        label = str(item.get("action_label", "")).strip()
        if label:
            label_map[step_id] = label
    if not label_map:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Orchestrator AI labeling produced no usable action labels.",
        )

    labeled: list[dict] = []
    for step in trace:
        sid = int(step.get("step_id", 0))
        action_key = str(step.get("action", "")).strip()
        step_copy = dict(step)
        step_copy["action_key"] = action_key
        step_copy["action"] = label_map.get(sid, action_key)
        labeled.append(step_copy)
    return labeled


def _synthesize_final(goal: str, target_role: str, constraints: str, trace: list[dict], artifacts: dict) -> dict:
    trace_summary = [
        {
            "step_id": step.get("step_id"),
            "agent": step.get("agent"),
            "action": step.get("action"),
            "status": step.get("status"),
            "output": _compact_for_prompt(step.get("output", {})),
        }
        for step in trace
    ]
    prompt = (
        "You are an orchestration summarizer for career planning.\n"
        f"goal={goal}\n"
        f"target_role={target_role}\n"
        f"constraints={constraints}\n"
        f"trace={_compact_json_text(trace_summary, max_chars=2400)}\n"
        f"artifacts={_compact_json_text(artifacts, max_chars=2400)}\n"
        'Return JSON object: {"role_cluster":"...", "summary":"...", '
        '"next_best_actions":["...","...","..."], "risk_flags":["..."], "confidence": 0-100}. '
        "Actions must be specific to this run context."
    )
    data = generate_json(prompt)
    actions = data.get("next_best_actions", [])
    if not isinstance(actions, list) or len(actions) < 3:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Orchestrator AI synthesis returned insufficient next_best_actions.",
        )
    return {
        "role_cluster": str(data.get("role_cluster", infer_role_cluster(target_role or goal))).strip() or infer_role_cluster(target_role or goal),
        "summary": str(data.get("summary", "")).strip(),
        "next_best_actions": [str(a).strip() for a in actions if str(a).strip()][:6],
        "risk_flags": [str(r).strip() for r in (data.get("risk_flags", []) if isinstance(data.get("risk_flags"), list) else []) if str(r).strip()][:5],
        "confidence": int(data.get("confidence", 0)) if str(data.get("confidence", "")).strip().isdigit() else 0,
        "artifacts": artifacts,
    }


def orchestrate_goal(
    db: Session,
    user_id: UUID,
    goal: str,
    target_role: str = "",
    constraints: str = "",
    include_resources: bool = True,
    include_progress: bool = True,
) -> dict:
    plan = _build_plan(goal=goal, target_role=target_role, include_resources=include_resources, include_progress=include_progress)

    trace: list[dict] = []
    context_snapshot = {
        "goal": goal,
        "target_role": target_role,
        "constraints": constraints,
        "created_at": datetime.utcnow().isoformat(),
    }

    for idx, step in enumerate(plan, start=1):
        step_result = _execute_step(
            db=db,
            user_id=user_id,
            step=step,
            goal=goal,
            target_role=target_role,
            constraints=constraints,
        )
        trace.append(_json_safe({"step_id": idx, **step_result}))

    trace = _label_trace_actions(
        trace=trace,
        goal=goal,
        target_role=target_role,
        constraints=constraints,
    )

    artifacts = {
        "resume": next((t["output"] for t in trace if t["agent"] == "resume_agent"), {}),
        "career": next((t["output"] for t in trace if t["agent"] == "career_agent"), {}),
        "interview": next((t["output"] for t in trace if t["agent"] == "interview_agent"), {}),
        "resources": next((t["output"] for t in trace if t["agent"] == "resource_agent"), {}),
        "progress": next((t["output"] for t in trace if t["agent"] == "progress_agent"), {}),
    }
    final = _synthesize_final(
        goal=goal,
        target_role=target_role,
        constraints=constraints,
        trace=trace,
        artifacts=artifacts,
    )

    safe_plan = _json_safe({"steps": plan})
    safe_context = _json_safe(context_snapshot)
    safe_result = _json_safe({"trace": trace, "final": final})

    row = AgentRun(
        user_id=user_id,
        goal=goal,
        status="completed",
        plan=safe_plan,
        context_snapshot=safe_context,
        result=safe_result,
    )
    db.add(row)
    db.commit()
    db.refresh(row)

    return {
        "run_id": row.id,
        "goal": goal,
        "status": row.status,
        "plan": plan,
        "trace": trace,
        "result": final,
        "created_at": row.created_at,
    }
