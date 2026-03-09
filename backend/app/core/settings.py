from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "VidyaMitra API"
    database_url: str = "sqlite:///./vidyamitra.db"
    secret_key: str = "change-this-secret-in-env"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    cors_origins: str = "http://localhost:5173"
    # Preferred names for Groq provider.
    groq_api_key: str = ""
    groq_model: str = "llama-3.1-8b-instant"
    groq_base_url: str = "https://api.groq.com/openai/v1"
    # Backward-compatible aliases.
    grok_api_key: str = ""
    grok_model: str = "grok-2-latest"
    grok_base_url: str = "https://api.x.ai/v1"
    google_api_key: str = ""
    google_cse_id: str = ""
    youtube_api_key: str = ""
    pexels_api_key: str = ""
    news_api_key: str = ""
    exchange_api_key: str = ""
    supabase_url: str = ""
    supabase_key: str = ""
    supabase_service_role_key: str = ""
    supabase_bucket: str = "uploads"

    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).resolve().parents[2] / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
