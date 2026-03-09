from pydantic import BaseModel, Field


class CareerSupportRequest(BaseModel):
    goal: str = Field(min_length=3, max_length=300)
    background: str = Field(default="", max_length=2000)
    target_role: str = Field(default="", max_length=150)
    constraints: str = Field(default="", max_length=1000)


class LearningResourcesResponse(BaseModel):
    youtube: list[dict]
    google: list[dict]


class VisualResourcesResponse(BaseModel):
    images: list[dict]


class MarketResourcesResponse(BaseModel):
    news: list[dict]
    exchange: dict


class ProfileSyncRequest(BaseModel):
    profile_data: dict


class StorageUploadRequest(BaseModel):
    filename: str = Field(min_length=3, max_length=255)
    content_base64: str = Field(min_length=1)
    content_type: str = "application/octet-stream"
    bucket: str | None = None
