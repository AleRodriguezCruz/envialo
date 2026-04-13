from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional

class Settings(BaseSettings):
    # --- Configuración General ---
    APP_ENV: str = "development"
    APP_PORT: int = 8000
    SECRET_KEY: str
    
    # --- Archivos y Reglas ---
    MAX_FILE_SIZE: int = 104857600
    TRANSFER_EXPIRY_HOURS: int = 72
    CLEANUP_INTERVAL_HOURS: int = 6
    ALLOWED_MIME_TYPES: str = "image/jpeg,image/png,image/gif,image/webp,application/pdf,application/zip,text/plain,video/mp4,audio/mpeg"

    # --- Base de Datos (PostgreSQL) ---
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    # --- Almacenamiento (Supabase) ---
    SUPABASE_URL: str
    SUPABASE_ANON_KEY: str
    SUPABASE_SERVICE_KEY: str
    SUPABASE_BUCKET: str = "transfers"

    # --- Correo (SMTP / Gmail) ---
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str          # Tu correo de Gmail
    SMTP_PASSWORD: str      # Tu contraseña de aplicación de 16 letras
    SMTP_FROM_NAME: str = "Envialo 📦"

    # --- Variables obsoletas (Para evitar errores si siguen en el .env) ---
    RESEND_API_KEY: Optional[str] = ""
    RESEND_FROM_EMAIL: Optional[str] = "onboarding@resend.dev"

    # --- Propiedades Dinámicas ---
    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def ALLOWED_MIME_TYPES_LIST(self) -> list[str]:
        return [mime.strip() for mime in self.ALLOWED_MIME_TYPES.split(",")]

    # --- Configuración de Pydantic ---
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # Esto evita el error de "Extra inputs are not permitted"


@lru_cache()
def get_settings() -> Settings:
    return Settings()

# Instancia global para usar en toda la app
settings = get_settings()