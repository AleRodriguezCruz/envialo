# =============================================================================
# deps.py — Dependencias compartidas de FastAPI
# Provee la sesión de DB y la IP del cliente a los endpoints
# =============================================================================
from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.postgres import get_db


# -----------------------------------------------------------------------------
# Dependencia de base de datos
# Cada request obtiene su propia sesión
# -----------------------------------------------------------------------------
async def get_db_session(db: AsyncSession = Depends(get_db)) -> AsyncSession:
    return db


# -----------------------------------------------------------------------------
# Obtiene la IP real del cliente
# Considera proxies y load balancers
# -----------------------------------------------------------------------------
def get_client_ip(request: Request) -> str | None:
    # Intenta obtener la IP real detrás de un proxy
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.client.host if request.client else None