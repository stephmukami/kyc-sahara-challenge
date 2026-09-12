from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "KYC Orchestrator"
    environment: str = "development"

    database_url: str = "postgresql+asyncpg://kyc:kyc@localhost:5432/kyc_orchestrator"

    cors_origins: list[str] = ["http://localhost:3000"]

    jwt_secret_key: str = "dev-secret-change-me"
    jwt_algorithm: str = "HS256"
    access_token_ttl_minutes: int = 30
    refresh_token_ttl_days: int = 30

    otp_ttl_minutes: int = 5
    otp_length: int = 6
    otp_max_attempts: int = 5

    password_reset_token_ttl_minutes: int = 30

    africastalking_username: str | None = None
    africastalking_api_key: str | None = None
    africastalking_sender_id: str | None = None
    africastalking_voice_number: str | None = None


@lru_cache
def get_settings() -> Settings:
    return Settings()
