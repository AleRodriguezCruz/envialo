# =============================================================================
# transfer_repo.py — Repositorio de Transfers
# Patrón Repository: encapsula todas las operaciones de DB para transfers
# Los servicios llaman a este repositorio, nunca a SQLAlchemy directamente
# =============================================================================
from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models.transfer import Transfer


class TransferRepository:

    def __init__(self, db: AsyncSession):
        # Recibe la sesión de DB por inyección de dependencias
        self.db = db

    # -------------------------------------------------------------------------
    # CREAR un nuevo transfer
    # -------------------------------------------------------------------------
    async def create(self, token: str, expires_at: datetime, message: str | None = None) -> Transfer:
        transfer = Transfer(
            token=token,
            message=message,
            expires_at=expires_at,
            is_active=True,
            download_count=0
        )
        self.db.add(transfer)
        await self.db.flush()  # flush para obtener el ID sin hacer commit
        await self.db.refresh(transfer)
        return transfer

    # -------------------------------------------------------------------------
    # BUSCAR transfer por token (incluye sus archivos)
    # -------------------------------------------------------------------------
    async def get_by_token(self, token: str) -> Transfer | None:
        result = await self.db.execute(
            select(Transfer)
            .where(Transfer.token == token)
            .options(selectinload(Transfer.files))  # Carga los archivos relacionados
        )
        return result.scalar_one_or_none()

    # -------------------------------------------------------------------------
    # BUSCAR transfers expirados (para el worker de limpieza)
    # -------------------------------------------------------------------------
    async def get_expired_active(self) -> list[Transfer]:
        now = datetime.now(timezone.utc)
        result = await self.db.execute(
            select(Transfer)
            .where(Transfer.is_active == True)
            .where(Transfer.expires_at < now)
            .options(selectinload(Transfer.files))
        )
        return list(result.scalars().all())

    # -------------------------------------------------------------------------
    # MARCAR transfer como eliminado/expirado
    # -------------------------------------------------------------------------
    async def mark_as_deleted(self, token: str) -> bool:
        now = datetime.now(timezone.utc)
        result = await self.db.execute(
            update(Transfer)
            .where(Transfer.token == token)
            .values(
                is_active=False,
                deleted_at=now
            )
        )
        return result.rowcount > 0

    # -------------------------------------------------------------------------
    # INCREMENTAR contador de descargas
    # -------------------------------------------------------------------------
    async def increment_download_count(self, token: str) -> None:
        transfer = await self.get_by_token(token)
        if transfer:
            transfer.download_count += 1
            await self.db.flush()