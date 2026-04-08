# =============================================================================
# files.py — Endpoints GET /file/{token} y DELETE /file/{token}
# GET: retorna la información del transfer sin generar URLs de descarga
# DELETE: elimina el transfer y sus archivos de Supabase Storage
# =============================================================================
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db_session, get_client_ip
from app.services.download_service import DownloadService

router = APIRouter()


@router.get("/file/{token}", summary="Obtener información del transfer")
async def get_file_info(
    token: str,
    request: Request,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Retorna la información pública del transfer sin generar URLs de descarga.
    Útil para mostrar la vista previa antes de descargar.

    - 404 si el token no existe
    - 410 si el transfer expiró o fue eliminado
    """
    service = DownloadService(db)
    return await service.get_transfer_info(token=token)


@router.delete("/file/{token}", summary="Eliminar un transfer")
async def delete_file(
    token: str,
    request: Request,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Elimina un transfer y todos sus archivos de Supabase Storage.

    - Elimina los archivos binarios de Supabase Storage
    - Marca el transfer como eliminado en PostgreSQL
    - Registra el evento en audit_logs
    - 404 si el token no existe
    - 410 si ya fue eliminado
    """
    ip_address = get_client_ip(request)
    service = DownloadService(db)
    return await service.delete_transfer(token=token, ip_address=ip_address)