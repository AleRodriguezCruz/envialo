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
        self.transfer_repo = TransferRepository(db)
        self.file_repo = FileRepository(db)
        self.storage = StorageService()
        self.audit = AuditService()

    async def upload(
        self,
        file_content: bytes,
        original_filename: str,
        message: str | None = None,
        ip_address: str | None = None,
        recipient_email: str | None = None
    ) -> dict:

        safe_filename = sanitize_filename(original_filename)

        if is_executable_file(safe_filename):
            raise ExecutableFileException(safe_filename)

        if not validate_file_size(len(file_content)):
            max_mb = settings.MAX_FILE_SIZE // (1024 * 1024)
            raise FileTooLargeException(max_mb)

        is_valid_mime, detected_mime = validate_mime_type(file_content)
        if not is_valid_mime:
            raise UnsupportedFileTypeException(detected_mime)

        token = generate_transfer_token()
        expires_at = datetime.now(timezone.utc) + timedelta(
            hours=settings.TRANSFER_EXPIRY_HOURS
        )

        storage_path = f"transfers/{token}/{safe_filename}"

        await self.storage.upload_file(
            storage_path=storage_path,
            file_content=file_content,
            mime_type=detected_mime
        )

        transfer = await self.transfer_repo.create(
            token=token,
            expires_at=expires_at,
            message=message
        )

        await self.file_repo.create(
            transfer_id=transfer.id,
            original_filename=safe_filename,
            mime_type=detected_mime,
            file_size=len(file_content),
            storage_path=storage_path
        )

        await self.audit.log_upload(
            token=token,
            filename=safe_filename,
            ip=ip_address
        )

        share_url = f"http://localhost:8000?token={token}"

        if recipient_email:
            from app.services.email_service import EmailService
            email_svc = EmailService()
            await email_svc.send_download_link(
                to_email=recipient_email,
                download_url=share_url,
                filename=safe_filename,
                message=message,
                expires_at=expires_at.strftime("%d/%m/%Y %H:%M")
            )

        return {
            "token": token,
            "filename": safe_filename,
            "mime_type": detected_mime,
            "file_size": len(file_content),
            "expires_at": expires_at.isoformat(),
            "download_url": share_url,
            "email_sent": bool(recipient_email)
        }