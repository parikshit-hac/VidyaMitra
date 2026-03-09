from __future__ import annotations

import re
from fastapi import HTTPException, status

SKILL_SYNONYMS: dict[str, list[str]] = {
    "sql": ["sql", "postgresql", "mysql", "sql server"],
    "excel": ["excel", "spreadsheet"],
    "statistics": ["statistics", "hypothesis testing", "probability", "regression"],
    "python": ["python", "numpy", "pandas", "matplotlib", "seaborn"],
    "pandas": ["pandas"],
    "power bi": ["power bi", "powerbi"],
    "tableau": ["tableau"],
    "machine learning": ["machine learning", "ml", "classification", "clustering"],
    "feature engineering": ["feature engineering"],
    "model deployment": ["model deployment", "mlops", "serving"],
    "communication": ["communication", "presentation", "storytelling"],
    "requirement analysis": ["requirement analysis", "requirements gathering", "brd", "frd"],
    "stakeholder management": ["stakeholder management", "stakeholder communication"],
    "network security": ["network security", "firewall", "ids", "ips", "network hardening"],
    "siem": ["siem", "splunk", "qradar", "sentinel"],
    "incident response": ["incident response", "forensics", "triage"],
    "threat modeling": ["threat modeling", "stride"],
    "vulnerability assessment": ["vulnerability assessment", "vulnerability management", "nessus"],
    "penetration testing": ["penetration testing", "pentest", "ethical hacking"],
    "linux": ["linux", "bash", "shell scripting"],
    "iam": ["iam", "identity and access management", "rbac", "oauth"],
    "cloud security": ["cloud security", "aws security", "azure security", "gcp security"],
    "data structures": ["data structures", "arrays", "linked list", "trees", "hashmap"],
    "algorithms": ["algorithms", "complexity", "sorting", "searching", "dynamic programming"],
    "javascript": ["javascript", "js", "typescript", "node.js", "react"],
    "api development": ["api", "rest", "fastapi", "express", "graphql"],
    "git": ["git", "github", "gitlab"],
    "testing": ["testing", "unit test", "integration test", "pytest", "jest"],
    "docker": ["docker", "container"],
    "kubernetes": ["kubernetes", "k8s"],
    "ci/cd": ["ci/cd", "github actions", "jenkins", "gitlab ci"],
    "monitoring": ["monitoring", "grafana", "prometheus", "observability"],
    "automation": ["automation", "scripting"],
    "roadmapping": ["roadmap", "roadmapping", "prioritization"],
}


def _normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().lower())


def infer_role_cluster(target_role: str) -> str:
    text = _normalize_text(target_role)
    return text or "general"


def _unique_ordered(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        key = _normalize_text(item)
        if key and key not in seen:
            seen.add(key)
            out.append(item.strip())
    return out


def _heuristic_required_skills(target_role: str, context_text: str = "") -> list[str]:
    # Strict AI mode: heuristic is only a shape guard, not a data source.
    role_tokens = [t for t in re.findall(r"[a-zA-Z]{3,}", _normalize_text(target_role))]
    context_tokens = [t for t in re.findall(r"[a-zA-Z]{3,}", _normalize_text(context_text))]
    merged = _unique_ordered(role_tokens + context_tokens)
    return merged[:10]


def required_skills_for_role(target_role: str, context_text: str = "") -> list[str]:
    role_text = _normalize_text(target_role)
    if not role_text:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="target_role is required")

    from app.services.grok_service import generate_json

    payload = generate_json(
        "Infer top skills for a job role.\n"
        f"target_role={target_role}\n"
        f"context={context_text[:4000]}\n"
        'Return JSON object: {"skills":["skill1","skill2",...]} with 8-12 concise technical/professional skills.'
    )
    raw = payload.get("skills", [])
    if not isinstance(raw, list):
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Grok skills response missing 'skills' list.")

    parsed = _unique_ordered([str(item).strip() for item in raw if str(item).strip()])
    if len(parsed) < 5:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Grok returned insufficient skills for target role.",
        )
    return parsed[:12]


def extract_skills_from_text(text: str, candidate_skills: list[str] | None = None) -> list[str]:
    lowered = _normalize_text(text)
    candidates = candidate_skills or list(SKILL_SYNONYMS.keys())
    found: list[str] = []
    for skill in candidates:
        aliases = SKILL_SYNONYMS.get(skill.lower(), [skill.lower()])
        if any(alias in lowered for alias in aliases):
            found.append(skill)
    return sorted(set(found), key=lambda x: x.lower())


def skill_gaps(current_skills: list[str], target_skills: list[str]) -> list[str]:
    current = {_normalize_text(s) for s in current_skills}
    return [s for s in target_skills if _normalize_text(s) not in current]
