from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    APP_ENV: str = "development"
    APP_PORT: int = 8000
    MAX_FILE_SIZE: int = 104857600
    TRANSFER_EXPIRY_HOURS: int = 72
    ALLOWED_MIME_TYPES: str = "image/jpeg,image/png,image/gif,image/webp,application/pdf,application/zip,text/plain,video/mp4,audio/mpeg"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    SUPABASE_URL: str
    SUPABASE_ANON_KEY: str
    SUPABASE_SERVICE_KEY: str
    SUPABASE_BUCKET: str = "transfers"
    SECRET_KEY: str
    RESEND_API_KEY: str = ""
    RESEND_FROM_EMAIL: str = "onboarding@resend.dev"
    CLEANUP_INTERVAL_HOURS: int = 6

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def ALLOWED_MIME_TYPES_LIST(self) -> list[str]:
        return [mime.strip() for mime in self.ALLOWED_MIME_TYPES.split(",")]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()