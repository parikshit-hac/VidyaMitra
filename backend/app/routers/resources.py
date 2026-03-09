from fastapi import APIRouter, Depends

from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.integration_schema import (
    LearningResourcesResponse,
    MarketResourcesResponse,
    ProfileSyncRequest,
    StorageUploadRequest,
    VisualResourcesResponse,
)
from app.services.news_service import get_exchange_rates, search_news
from app.services.pexels_service import search_images
from app.services.supabase_service import get_recent_profile_updates, sync_profile_data, upload_file_base64
from app.services.youtube_service import search_google_resources, search_youtube


router = APIRouter(prefix="/resources", tags=["Resources"])


@router.get("/health")
def resources_health(_: User = Depends(get_current_user)) -> dict[str, str]:
    return {"message": "Resources router ready"}


@router.get("/learning", response_model=LearningResourcesResponse)
def learning_resources(topic: str, _: User = Depends(get_current_user)) -> LearningResourcesResponse:
    youtube_results = search_youtube(query=topic)
    google_results = search_google_resources(query=f"{topic} course roadmap tutorial")
    return LearningResourcesResponse(youtube=youtube_results, google=google_results)


@router.get("/visuals", response_model=VisualResourcesResponse)
def visual_resources(query: str, _: User = Depends(get_current_user)) -> VisualResourcesResponse:
    return VisualResourcesResponse(images=search_images(query=query))


@router.get("/market", response_model=MarketResourcesResponse)
def market_resources(
    topic: str = "job market",
    base_currency: str = "USD",
    symbols: str = "INR,EUR",
    _: User = Depends(get_current_user),
) -> MarketResourcesResponse:
    return MarketResourcesResponse(news=search_news(topic), exchange=get_exchange_rates(base_currency, symbols))


@router.post("/sync/profile")
def profile_sync(payload: ProfileSyncRequest, user: User = Depends(get_current_user)) -> dict:
    return sync_profile_data(user.id, payload.profile_data)


@router.post("/storage/upload")
def storage_upload(payload: StorageUploadRequest, user: User = Depends(get_current_user)) -> dict:
    return upload_file_base64(
        user_id=user.id,
        filename=payload.filename,
        content_base64=payload.content_base64,
        content_type=payload.content_type,
        bucket=payload.bucket,
    )


@router.get("/sync/recent")
def recent_sync(limit: int = 20, _: User = Depends(get_current_user)) -> dict:
    return {"users": get_recent_profile_updates(limit=limit)}
