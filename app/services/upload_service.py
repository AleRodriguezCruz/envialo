# =============================================================================
# upload_service.py — Servicio de subida de archivos
# Responsabilidad: orquesta todo el flujo de subida:
# 1. Valida el archivo (tamaño, MIME, ejecutables)
# 2. Lo sube a Supabase Storage
# 3. Guarda la metadata en PostgreSQL
# 4. Registra el evento en audit_logs
# =============================================================================
from datetime import datetime, timezone, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import (
    generate_transfer_token,
    validate_mime_type,
    validate_file_size,
    sanitize_filename,
    is_executable_file
)
from app.core.exceptions import (
    FileTooLargeException,
    UnsupportedFileTypeException,
    ExecutableFileException
)
from app.repositories.transfer_repo import TransferRepository
from app.repositories.file_repo import FileRepository
from app.services.storage_service import StorageService
from app.services.audit_service import AuditService


class UploadService:

    def __init__(self, db: AsyncSession):
        # Inyecta la sesión de DB y crea los repositorios y servicios necesarios
        self.transfer_repo = TransferRepository(db)
        self.file_repo = FileRepository(db)
        self.storage = StorageService()
        self.audit = AuditService()

    # -------------------------------------------------------------------------
    # FLUJO COMPLETO DE SUBIDA
    # -------------------------------------------------------------------------
    async def upload(
        self,
        file_content: bytes,
        original_filename: str,
        message: str | None = None,
        ip_address: str | None = None
    ) -> dict:

        # ---------------------------------------------------------------------
        # PASO 1: Sanitiza el nombre del archivo
        # ---------------------------------------------------------------------
        safe_filename = sanitize_filename(original_filename)

        # ---------------------------------------------------------------------
        # PASO 2: Verifica que no sea un ejecutable
        # ---------------------------------------------------------------------
        if is_executable_file(safe_filename):
            raise ExecutableFileException(safe_filename)

        # ---------------------------------------------------------------------
        # PASO 3: Valida el tamaño del archivo
        # ---------------------------------------------------------------------
        if not validate_file_size(len(file_content)):
            max_mb = settings.MAX_FILE_SIZE // (1024 * 1024)
            raise FileTooLargeException(max_mb)

        # ---------------------------------------------------------------------
        # PASO 4: Valida el tipo MIME con magic bytes reales
        # ---------------------------------------------------------------------
        is_valid_mime, detected_mime = validate_mime_type(file_content)
        if not is_valid_mime:
            raise UnsupportedFileTypeException(detected_mime)

        # ---------------------------------------------------------------------
        # PASO 5: Genera token seguro y fecha de expiración
        # ---------------------------------------------------------------------
        token = generate_transfer_token()
        expires_at = datetime.now(timezone.utc) + timedelta(
            hours=settings.TRANSFER_EXPIRY_HOURS
        )

        # ---------------------------------------------------------------------
        # PASO 6: Define la ruta en Supabase Storage
        # Formato: transfers/{token}/{filename}
        # ---------------------------------------------------------------------
        storage_path = f"transfers/{token}/{safe_filename}"

        # ---------------------------------------------------------------------
        # PASO 7: Sube el archivo a Supabase Storage
        # ---------------------------------------------------------------------
        await self.storage.upload_file(
            storage_path=storage_path,
            file_content=file_content,
            mime_type=detected_mime
        )

        # ---------------------------------------------------------------------
        # PASO 8: Guarda el transfer en PostgreSQL
        # ---------------------------------------------------------------------
        transfer = await self.transfer_repo.create(
            token=token,
            expires_at=expires_at,
            message=message
        )

        # ---------------------------------------------------------------------
        # PASO 9: Guarda la metadata del archivo en PostgreSQL
        # ---------------------------------------------------------------------
        file = await self.file_repo.create(
            transfer_id=transfer.id,
            original_filename=safe_filename,
            mime_type=detected_mime,
            file_size=len(file_content),
            storage_path=storage_path
        )

        # ---------------------------------------------------------------------
        # PASO 10: Registra el evento en audit_logs de Supabase
        # ---------------------------------------------------------------------
        await self.audit.log_upload(
            token=token,
            filename=safe_filename,
            ip=ip_address
        )

        # ---------------------------------------------------------------------
        # Retorna la información del transfer creado
        # ---------------------------------------------------------------------
        return {
            "token": token,
            "filename": safe_filename,
            "mime_type": detected_mime,
            "file_size": len(file_content),
            "expires_at": expires_at.isoformat(),
            "download_url": f"/download/{token}"
        }