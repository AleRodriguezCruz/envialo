# =============================================================================
# upload.py — Endpoint POST /upload
# Recibe el archivo, lo valida y lo sube a Supabase Storage
# =============================================================================
from fastapi import APIRouter, Depends, UploadFile, File, Form, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db_session, get_client_ip
from app.services.upload_service import UploadService

router = APIRouter()


@router.post("/upload", summary="Subir un archivo")
async def upload_file(
    request: Request,
    file: UploadFile = File(..., description="Archivo a subir"),
    message: str | None = Form(None, description="Mensaje opcional del remitente"),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Sube un archivo y retorna el token de descarga.

    - Valida el tipo MIME con magic bytes reales
    - Bloquea archivos ejecutables
    - Limita el tamaño según MAX_FILE_SIZE
    - Guarda el archivo en Supabase Storage
    - Registra la metadata en PostgreSQL
    """
    # Lee el contenido del archivo en memoria
    file_content = await file.read()

    # Obtiene la IP del cliente para el audit log
    ip_address = get_client_ip(request)

    # Ejecuta el flujo completo de subida
    service = UploadService(db)
    result = await service.upload(
        file_content=file_content,
        original_filename=file.filename or "archivo_sin_nombre",
        message=message,
        ip_address=ip_address
    )

    return result