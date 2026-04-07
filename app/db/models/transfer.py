# =============================================================================
# transfer.py — Modelo de Transfer
# Representa un "paquete" de envío que agrupa uno o más archivos
# Se almacena en PostgreSQL local
# =============================================================================
import uuid
from datetime import datetime, timezone

from sqlalchemy import String, DateTime, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.postgres import Base


class Transfer(Base):
    __tablename__ = "transfers"

    # -------------------------------------------------------------------------
    # Columnas principales
    # -------------------------------------------------------------------------

    # ID interno autoincremental (uso interno, no se expone al usuario)
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Token único que identifica el transfer (se comparte con el usuario)
    token: Mapped[str] = mapped_column(
        String(200),
        unique=True,
        nullable=False,
        index=True  # Índice para búsquedas rápidas por token
    )

    # Mensaje opcional del remitente
    message: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # -------------------------------------------------------------------------
    # Estado del transfer
    # -------------------------------------------------------------------------

    # True = el transfer está activo y disponible para descargar
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Número de veces que se han descargado los archivos
    download_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # -------------------------------------------------------------------------
    # Fechas
    # -------------------------------------------------------------------------

    # Fecha de creación (se establece automáticamente)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Fecha de expiración (creado_at + TRANSFER_EXPIRY_HOURS)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )

    # Fecha en que fue eliminado (None si aún está activo)
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    # -------------------------------------------------------------------------
    # Relación con archivos (un transfer puede tener múltiples archivos)
    # -------------------------------------------------------------------------
    files: Mapped[list["File"]] = relationship(
        "File",
        back_populates="transfer",
        cascade="all, delete-orphan"  # Si se borra el transfer, se borran sus archivos
    )

    def __repr__(self) -> str:
        return f"<Transfer token={self.token[:20]}... active={self.is_active}>"