from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.progress_schema import ProgressDashboardResponse
from app.services.progress_service import get_progress_dashboard, sync_progress


router = APIRouter(prefix="/progress", tags=["Progress"])


@router.get("/dashboard", response_model=ProgressDashboardResponse)
def progress_dashboard(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProgressDashboardResponse:
    return get_progress_dashboard(db=db, user_id=user.id)


@router.post("/sync")
def progress_sync(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    return sync_progress(db=db, user_id=user.id)
