from datetime import datetime
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.resume import Resume
from app.services.grok_service import generate_career_support, generate_json
from app.services.youtube_service import search_youtube
from app.utils.dynamic_engine import extract_skills_from_text, required_skills_for_role, skill_gaps
from app.utils.file_parser import extract_text_from_pdf, save_uploaded_pdf

def _youtube_recommendations(skill_gaps: list[str], target_role: str) -> list[dict]:
    recommendations: list[dict] = []
    seen_urls: set[str] = set()
    for skill in skill_gaps[:5]:
        try:
            queries = [
                f"{skill} tutorial for {target_role}",
                f"{skill} projects and interview prep",
            ]
            for query in queries:
                yt_results = search_youtube(query, max_results=2)
                for item in yt_results:
                    url = str(item.get("url", "")).strip()
                    if not url or url in seen_urls:
                        continue
                    seen_urls.add(url)
                    recommendations.append({"skill": skill, **item, "provider": "YouTube"})
                    if len(recommendations) >= 12:
                        return recommendations
        except HTTPException:
            continue
    return recommendations


def upload_resume_pdf(db: Session, user_id: UUID, filename: str, file_bytes: bytes) -> dict:
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only PDF files are allowed")
    if not file_bytes:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Empty file")

    file_path = save_uploaded_pdf(file_bytes=file_bytes, original_filename=filename, user_id=user_id)
    extracted_text = extract_text_from_pdf(file_bytes)

    meta = {
        "extracted_text": extracted_text,
        "analysis": {},
    }
    row = Resume(
        user_id=user_id,
        title=filename,
        file_url=file_path,
        is_active=True,
        meta=meta,
    )
    db.add(row)
    db.commit()
    db.refresh(row)

    return {
        "resume_id": row.id,
        "title": row.title or filename,
        "file_url": row.file_url or "",
        "extracted_chars": len(extracted_text),
        "message": "Resume uploaded and parsed successfully",
    }


def analyze_resume(db: Session, user_id: UUID, resume_id: UUID, target_role: str) -> dict:
    row = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == user_id).first()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")

    meta = row.meta or {}
    resume_text = str(meta.get("extracted_text", "")).strip()
    if not resume_text:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No extracted text found for this resume")

    target_skills = required_skills_for_role(target_role, context_text=resume_text)
    identified_skills = extract_skills_from_text(resume_text, target_skills)
    missing_skills = skill_gaps(identified_skills, target_skills)

    ai_map = generate_json(
        "Analyze resume and return skill mapping JSON.\n"
        f"target_role={target_role}\n"
        f"resume_text={resume_text[:12000]}\n"
        'Return {"identified_skills":[...], "target_skills":[...], "skill_gaps":[...], "summary":"..."}'
    )
    ai_identified = ai_map.get("identified_skills", [])
    ai_target = ai_map.get("target_skills", [])
    ai_gaps = ai_map.get("skill_gaps", [])
    if not isinstance(ai_target, list) or not ai_target:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Groq resume response missing target_skills.")
    if not isinstance(ai_identified, list) or not ai_identified:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Groq resume response missing identified_skills.")
    if not isinstance(ai_gaps, list):
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Groq resume response missing skill_gaps.")
    target_skills = [str(x).strip() for x in ai_target if str(x).strip()][:15]
    identified_skills = [str(x).strip() for x in ai_identified if str(x).strip()][:20]
    missing_skills = [str(x).strip() for x in ai_gaps if str(x).strip()][:15]

    recommendations = _youtube_recommendations(missing_skills, target_role=target_role)

    prompt = (
        "Evaluate this resume for employability and skill gap mapping.\n"
        f"Target role: {target_role}\n"
        f"Identified skills: {identified_skills}\n"
        f"Skill gaps: {missing_skills}\n"
        "Return concise actionable guidance."
    )
    ai_summary = generate_career_support(prompt)
    ai_source = "groq"

    analysis = {
        "target_role": target_role,
        "identified_skills": identified_skills,
        "skill_gaps": missing_skills,
        "recommended_courses": recommendations,
        "ai_summary": ai_summary,
        "ai_source": ai_source,
        "updated_at": datetime.utcnow().isoformat(),
    }
    meta["analysis"] = analysis
    row.meta = meta
    row.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(row)

    return {
        "resume_id": row.id,
        "target_role": target_role,
        "identified_skills": identified_skills,
        "skill_gaps": missing_skills,
        "recommended_courses": recommendations,
        "ai_summary": ai_summary,
        "ai_source": ai_source,
        "updated_at": row.updated_at,
    }


def get_resume_detail(db: Session, user_id: UUID, resume_id: UUID) -> dict:
    row = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == user_id).first()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")
    return {
        "id": row.id,
        "title": row.title,
        "file_url": row.file_url,
        "is_active": row.is_active,
        "metadata": row.meta or {},
        "created_at": row.created_at,
        "updated_at": row.updated_at,
    }


def list_resumes(db: Session, user_id: UUID, limit: int = 20) -> list[dict]:
    rows = (
        db.query(Resume)
        .filter(Resume.user_id == user_id)
        .order_by(Resume.updated_at.desc().nullslast(), Resume.created_at.desc().nullslast())
        .limit(max(1, min(limit, 100)))
        .all()
    )
    return [{"id": row.id, "title": row.title or "Untitled"} for row in rows]
