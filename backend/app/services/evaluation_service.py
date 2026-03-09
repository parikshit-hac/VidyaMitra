import re

from app.services.grok_service import generate_career_support
from app.utils.dynamic_engine import required_skills_for_role, skill_gaps


def build_resume_draft(
    full_name: str,
    target_role: str,
    professional_summary: str,
    skills: list[str],
    experiences: list[str],
    projects: list[str],
    education: list[str],
    certifications: list[str],
) -> dict:
    normalized_skills = [s.strip() for s in skills if s.strip()]
    role_keywords = required_skills_for_role(target_role)

    prompt = (
        "Create an ATS-friendly resume draft.\n"
        f"Name: {full_name}\nTarget role: {target_role}\nSummary: {professional_summary}\n"
        f"Skills: {normalized_skills}\nExperiences: {experiences}\nProjects: {projects}\n"
        f"Education: {education}\nCertifications: {certifications}\n"
        "Return concise professional language."
    )
    ai_summary = generate_career_support(prompt)
    source = "groq"

    headline = f"{target_role} | {', '.join(normalized_skills[:3])}" if normalized_skills else target_role
    experience_bullets = experiences if experiences else ["Add measurable impact bullets using action verbs and outcomes."]
    ats_keywords = sorted(set(role_keywords + normalized_skills))[:15]

    return {
        "full_name": full_name,
        "target_role": target_role,
        "headline": headline,
        "summary": ai_summary,
        "skills": normalized_skills,
        "experience_bullets": experience_bullets,
        "projects": projects,
        "education": education,
        "certifications": certifications,
        "ats_keywords": ats_keywords,
        "ai_source": source,
    }


def eligibility_assessment(target_role: str, current_skills: list[str], years_experience: float, education_level: str) -> dict:
    required = required_skills_for_role(target_role)
    normalized = {s.strip().lower() for s in current_skills if s.strip()}

    matched = [s for s in required if s.lower() in normalized]
    missing = skill_gaps(current_skills, required)

    skill_score = int((len(matched) / max(1, len(required))) * 70)
    exp_score = min(20, int(years_experience * 5))
    edu_bonus = 10 if education_level.strip().lower() in {"bachelor", "master", "mba", "phd"} else 5
    total = min(100, skill_score + exp_score + edu_bonus)

    recommendations: list[str] = []
    if missing:
        recommendations.append(f"Prioritize these missing skills: {', '.join(missing[:4])}.")
    if years_experience < 1:
        recommendations.append("Build practical projects to compensate for low experience.")
    recommendations.append("Align resume bullets with role-specific keywords and quantified outcomes.")

    matched_set = {m.lower() for m in matched}
    skill_breakdown = []
    for skill in required:
        score = 88 if skill.lower() in matched_set else 35
        skill_breakdown.append({"skill": skill, "score": score, "status": "matched" if score > 60 else "gap"})

    improvement_areas = [
        {
            "skill": skill,
            "priority": idx + 1,
            "tip": f"Spend 3 focused sessions this week on {skill} and build one mini project artifact."
        }
        for idx, skill in enumerate(missing[:6])
    ]

    return {
        "target_role": target_role,
        "eligibility_score": total,
        "matched_skills": matched,
        "missing_skills": missing,
        "skill_breakdown": skill_breakdown,
        "improvement_areas": improvement_areas,
        "criteria_breakdown": {
            "skill_score": skill_score,
            "experience_score": exp_score,
            "education_bonus": edu_bonus,
        },
        "recommendations": recommendations,
    }


def evaluate_content(category: str, content: str, target_role: str = "") -> dict:
    word_count = len(content.split())
    sentences = max(1, len(re.findall(r"[.!?]", content)))
    avg_sentence_len = word_count / sentences
    role_words = {w.lower() for w in re.findall(r"[a-zA-Z]{3,}", target_role)}
    content_words = {w.lower() for w in re.findall(r"[a-zA-Z]{3,}", content)}
    alignment = len(role_words & content_words)

    score = 45
    if word_count >= 120:
        score += 20
    elif word_count >= 70:
        score += 12
    if 10 <= avg_sentence_len <= 24:
        score += 15
    if alignment > 0:
        score += min(20, alignment * 4)
    score = max(20, min(98, score))

    strengths: list[str] = []
    improvements: list[str] = []
    next_steps: list[str] = []

    if word_count >= 120:
        strengths.append("Good depth in explanation.")
    else:
        improvements.append("Add more concrete details and outcomes.")

    if 10 <= avg_sentence_len <= 24:
        strengths.append("Readable sentence structure.")
    else:
        improvements.append("Improve readability with concise sentence lengths.")

    if alignment > 0:
        strengths.append("Includes role-aligned terminology.")
    else:
        improvements.append("Add target-role keywords for better relevance.")

    next_steps.append("Use STAR structure for examples with measurable impact.")
    next_steps.append("Add a concise closing statement with learning outcomes.")

    return {
        "category": category,
        "score": score,
        "strengths": strengths,
        "improvements": improvements,
        "next_steps": next_steps,
    }
