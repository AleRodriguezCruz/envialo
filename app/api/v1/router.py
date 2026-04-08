# =============================================================================
# router.py — Router principal de la API v1
# Agrupa todos los endpoints bajo el prefijo /api/v1
# =============================================================================
from fastapi import APIRouter

from app.api.v1 import upload, download, files

# Router principal que agrupa todos los sub-routers
api_router = APIRouter(prefix="/api/v1")

# Registra cada módulo de endpoints
api_router.include_router(upload.router, tags=["Upload"])
api_router.include_router(download.router, tags=["Download"])
api_router.include_router(files.router, tags=["Files"])