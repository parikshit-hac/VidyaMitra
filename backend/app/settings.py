from functools import lru_cache
from typing import Optional

from dotenv import load_dotenv
from pydantic import BaseModel
import os


load_dotenv()


class Settings(BaseModel):
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    google_api_key: Optional[str] = os.getenv("GOOGLE_API_KEY")
    youtube_api_key: Optional[str] = os.getenv("YOUTUBE_API_KEY")
    supabase_url: Optional[str] = os.getenv("SUPABASE_URL")
    supabase_key: Optional[str] = os.getenv("SUPABASE_KEY")
    pexels_api_key: Optional[str] = os.getenv("PEXELS_API_KEY")
    news_api_key: Optional[str] = os.getenv("NEWS_API_KEY")
    exchange_api_key: Optional[str] = os.getenv("EXCHANGE_API_KEY")
    jwt_secret: str = os.getenv("JWT_SECRET") or "change_me_in_env"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

