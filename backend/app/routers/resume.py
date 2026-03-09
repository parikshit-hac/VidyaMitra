from uuid import UUID

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.resume_schema import (
    ResumeAnalysisResponse,
    ResumeAnalyzeRequest,
    ResumeDetailResponse,
    ResumeSummary,
    ResumeUploadResponse,
)
from app.services.resume_service import analyze_resume, get_resume_detail, list_resumes, upload_resume_pdf


router = APIRouter(prefix="/resume", tags=["Resume"])


@router.get("/health")
def resume_health(_: User = Depends(get_current_user)) -> dict[str, str]:
    return {"message": "Resume router ready"}


@router.post("/upload", response_model=ResumeUploadResponse)
async def resume_upload(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ResumeUploadResponse:
    file_bytes = await file.read()
    result = upload_resume_pdf(
        db=db,
        user_id=user.id,
        filename=file.filename or "resume.pdf",
        file_bytes=file_bytes,
    )
    return ResumeUploadResponse(**result)


@router.post("/{resume_id}/analyze", response_model=ResumeAnalysisResponse)
def resume_analyze(
    resume_id: UUID,
    payload: ResumeAnalyzeRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ResumeAnalysisResponse:
    result = analyze_resume(db=db, user_id=user.id, resume_id=resume_id, target_role=payload.target_role)
    return ResumeAnalysisResponse(**result)


@router.get("/{resume_id}", response_model=ResumeDetailResponse)
def resume_get(
    resume_id: UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ResumeDetailResponse:
    result = get_resume_detail(db=db, user_id=user.id, resume_id=resume_id)
    return ResumeDetailResponse(**result)


@router.get("", response_model=list[ResumeSummary])
def resume_list(
    limit: int = 20,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ResumeSummary]:
    rows = list_resumes(db=db, user_id=user.id, limit=limit)
    return [ResumeSummary(**row) for row in rows]
