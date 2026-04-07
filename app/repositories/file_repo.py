# =============================================================================
# file_repo.py — Repositorio de Files
# Encapsula todas las operaciones de DB para archivos individuales
# =============================================================================
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.file import File


class FileRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    # -------------------------------------------------------------------------
    # CREAR un nuevo archivo asociado a un transfer
    # -------------------------------------------------------------------------
    async def create(
        self,
        transfer_id: int,
        original_filename: str,
        mime_type: str,
        file_size: int,
        storage_path: str
    ) -> File:
        file = File(
            transfer_id=transfer_id,
            original_filename=original_filename,
            mime_type=mime_type,
            file_size=file_size,
            storage_path=storage_path
        )
        self.db.add(file)
        await self.db.flush()
        await self.db.refresh(file)
        return file

    # -------------------------------------------------------------------------
    # BUSCAR archivos por transfer_id
    # -------------------------------------------------------------------------
    async def get_by_transfer_id(self, transfer_id: int) -> list[File]:
        result = await self.db.execute(
            select(File).where(File.transfer_id == transfer_id)
        )
        return list(result.scalars().all())

    # -------------------------------------------------------------------------
    # BUSCAR archivo por ID
    # -------------------------------------------------------------------------
    async def get_by_id(self, file_id: int) -> File | None:
        result = await self.db.execute(
            select(File).where(File.id == file_id)
        )
        return result.scalar_one_or_none()