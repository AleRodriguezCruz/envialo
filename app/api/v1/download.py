# =============================================================================
# download.py — Endpoint GET /download/{token}
# Retorna las URLs firmadas de Supabase para descargar los archivos
# =============================================================================
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db_session, get_client_ip
from app.services.download_service import DownloadService

router = APIRouter()


@router.get("/download/{token}", summary="Obtener URLs de descarga")
async def download_file(
    token: str,
    request: Request,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Retorna las URLs firmadas para descargar los archivos de un transfer.

    - Verifica que el token exista (404 si no existe)
    - Verifica que no haya expirado (410 si expiró)
    - Genera URLs firmadas con expiración de 1 hora
    - Incrementa el contador de descargas
    - Registra el evento en audit_logs
    """
    ip_address = get_client_ip(request)
    service = DownloadService(db)
    return await service.get_download_url(token=token, ip_address=ip_address)