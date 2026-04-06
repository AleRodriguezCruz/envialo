# =============================================================================
# config.py — Configuración central de la aplicación
# Lee todas las variables del archivo .env y las valida con Pydantic
# =============================================================================
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # -------------------------------------------------------------------------
    # Configuración general
    # -------------------------------------------------------------------------
    APP_ENV: str = "development"
    APP_PORT: int = 8000

    # Tamaño máximo de archivo en bytes (default 100 MB)
    MAX_FILE_SIZE: int = 104857600

    # Horas antes de que un transfer expire
    TRANSFER_EXPIRY_HOURS: int = 72

    # Tipos MIME permitidos separados por coma
    ALLOWED_MIME_TYPES: str = "image/jpeg,image/png,application/pdf"

    # -------------------------------------------------------------------------
    # PostgreSQL
    # -------------------------------------------------------------------------
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    # -------------------------------------------------------------------------
    # Supabase
    # -------------------------------------------------------------------------
    SUPABASE_URL: str
    SUPABASE_ANON_KEY: str
    SUPABASE_SERVICE_KEY: str
    SUPABASE_BUCKET: str = "transfers"

    # -------------------------------------------------------------------------
    # Seguridad
    # -------------------------------------------------------------------------
    SECRET_KEY: str

    # -------------------------------------------------------------------------
    # Worker de limpieza
    # -------------------------------------------------------------------------
    CLEANUP_INTERVAL_HOURS: int = 6

    # -------------------------------------------------------------------------
    # Propiedades calculadas — no vienen del .env
    # -------------------------------------------------------------------------
    @property
    def DATABASE_URL(self) -> str:
        # Construye la URL de conexión a PostgreSQL para SQLAlchemy async
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def ALLOWED_MIME_TYPES_LIST(self) -> list[str]:
        # Convierte el string separado por comas en una lista
        return [mime.strip() for mime in self.ALLOWED_MIME_TYPES.split(",")]

    class Config:
        # Le dice a Pydantic que lea las variables del archivo .env
        env_file = ".env"
        env_file_encoding = "utf-8"
        # Ignora variables extra que estén en .env pero no en esta clase
        extra = "ignore"


# -----------------------------------------------------------------------------
# Instancia global de configuración con caché
# lru_cache asegura que el .env solo se lea una vez durante toda la ejecución
# -----------------------------------------------------------------------------
@lru_cache()
def get_settings() -> Settings:
    return Settings()


# Acceso directo para importar en otros módulos
settings = get_settings()