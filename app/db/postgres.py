# =============================================================================
# postgres.py — Configuración de la conexión a PostgreSQL
# Usa SQLAlchemy async con asyncpg como driver
# =============================================================================
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


# -----------------------------------------------------------------------------
# Motor de base de datos async
# pool_pre_ping=True verifica que la conexión esté viva antes de usarla
# pool_size=10 — conexiones simultáneas máximas
# -----------------------------------------------------------------------------
engine = create_async_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    echo=settings.APP_ENV == "development",  # Muestra SQL en consola solo en dev
)


# -----------------------------------------------------------------------------
# Fábrica de sesiones async
# Cada request HTTP obtiene su propia sesión de base de datos
# autocommit=False — los cambios se confirman manualmente con await session.commit()
# -----------------------------------------------------------------------------
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,  # Evita queries extra después del commit
)


# -----------------------------------------------------------------------------
# Clase base para todos los modelos SQLAlchemy
# Todos los modelos deben heredar de esta clase
# -----------------------------------------------------------------------------
class Base(DeclarativeBase):
    pass


# -----------------------------------------------------------------------------
# Dependency de FastAPI — provee una sesión por request
# Se usa con Depends(get_db) en los endpoints
# -----------------------------------------------------------------------------
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()