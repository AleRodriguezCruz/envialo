# =============================================================================
# upload.py — Endpoint POST /upload
# =============================================================================
from fastapi import APIRouter, Depends, UploadFile, File, Form, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db_session, get_client_ip
from app.services.upload_service import UploadService

router = APIRouter()


@router.post("/upload", summary="Subir un archivo")
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
    message: str | None = Form(None),
    recipient_email: str | None = Form(None),
    db: AsyncSession = Depends(get_db_session)
):
    file_content = await file.read()
    ip_address = get_client_ip(request)

    service = UploadService(db)
    result = await service.upload(
        file_content=file_content,
        original_filename=file.filename or "archivo_sin_nombre",
        message=message,
        ip_address=ip_address,
        recipient_email=recipient_email
    )
    return result