# =============================================================================
# download_service.py — Servicio de descarga de archivos
# Responsabilidad: valida que el transfer exista y no haya expirado,
# genera URLs firmadas de Supabase para descarga segura y registra el evento
# =============================================================================
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import TransferNotFoundException, TransferExpiredException
from app.repositories.transfer_repo import TransferRepository
from app.services.storage_service import StorageService
from app.services.audit_service import AuditService


class DownloadService:

    def __init__(self, db: AsyncSession):
        self.transfer_repo = TransferRepository(db)
        self.storage = StorageService()
        self.audit = AuditService()

    # -------------------------------------------------------------------------
    # OBTENER información del transfer para la vista de descarga
    # -------------------------------------------------------------------------
    async def get_transfer_info(self, token: str) -> dict:
        # Busca el transfer en PostgreSQL
        transfer = await self.transfer_repo.get_by_token(token)

        # 404 si no existe
        if not transfer:
            raise TransferNotFoundException(token)

        # 410 si fue eliminado o expiró
        if not transfer.is_active or datetime.now(timezone.utc) > transfer.expires_at:
            raise TransferExpiredException(token)

        # Retorna la información pública del transfer
        return {
            "token": transfer.token,
            "message": transfer.message,
            "expires_at": transfer.expires_at.isoformat(),
            "download_count": transfer.download_count,
            "files": [
                {
                    "id": f.id,
                    "filename": f.original_filename,
                    "mime_type": f.mime_type,
                    "file_size": f.file_size
                }
                for f in transfer.files
            ]
        }

    # -------------------------------------------------------------------------
    # GENERAR URL firmada para descargar un archivo
    # Las URLs firmadas de Supabase expiran después de 1 hora
    # El archivo nunca se expone directamente — siempre via URL firmada
    # -------------------------------------------------------------------------
    async def get_download_url(
        self,
        token: str,
        ip_address: str | None = None
    ) -> list[dict]:
        # Busca y valida el transfer
        transfer = await self.transfer_repo.get_by_token(token)

        if not transfer:
            raise TransferNotFoundException(token)

        if not transfer.is_active or datetime.now(timezone.utc) > transfer.expires_at:
            raise TransferExpiredException(token)

        # Genera URLs firmadas para cada archivo del transfer
        download_urls = []
        for file in transfer.files:
            signed_url = await self.storage.create_signed_url(
                storage_path=file.storage_path,
                expires_in=3600  # URL válida por 1 hora
            )
            download_urls.append({
                "filename": file.original_filename,
                "mime_type": file.mime_type,
                "file_size": file.file_size,
                "download_url": signed_url
            })

            # Registra el evento de descarga en audit_logs
            await self.audit.log_download(
                token=token,
                filename=file.original_filename,
                ip=ip_address
            )

        # Incrementa el contador de descargas
        await self.transfer_repo.increment_download_count(token)

        return download_urls

    # -------------------------------------------------------------------------
    # ELIMINAR un transfer y sus archivos
    # -------------------------------------------------------------------------
    async def delete_transfer(
        self,
        token: str,
        ip_address: str | None = None
    ) -> dict:
        # Busca el transfer
        transfer = await self.transfer_repo.get_by_token(token)

        if not transfer:
            raise TransferNotFoundException(token)

        if not transfer.is_active:
            raise TransferExpiredException(token)

        # Obtiene las rutas de almacenamiento de todos los archivos
        storage_paths = [f.storage_path for f in transfer.files]

        # Elimina los archivos de Supabase Storage
        await self.storage.delete_transfer_files(storage_paths)

        # Marca el transfer como eliminado en PostgreSQL
        await self.transfer_repo.mark_as_deleted(token)

        # Registra el evento en audit_logs
        await self.audit.log_delete(token=token, ip=ip_address)

        return {"message": f"Transfer {token} eliminado correctamente"}