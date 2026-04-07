# =============================================================================
# file.py — Modelo de File
# Representa un archivo individual dentro de un Transfer
# Se almacena en PostgreSQL local (metadata)
# El binario real se guarda en Supabase Storage
# =============================================================================
from datetime import datetime, timezone

from sqlalchemy import String, DateTime, Integer, ForeignKey, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.postgres import Base


class File(Base):
    __tablename__ = "files"

    # -------------------------------------------------------------------------
    # Columnas principales
    # -------------------------------------------------------------------------

    # ID interno autoincremental
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Relación con el transfer padre
    transfer_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("transfers.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # -------------------------------------------------------------------------
    # Metadata del archivo
    # -------------------------------------------------------------------------

    # Nombre original del archivo (sanitizado)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)

    # Tipo MIME detectado con magic bytes
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)

    # Tamaño en bytes
    file_size: Mapped[int] = mapped_column(BigInteger, nullable=False)

    # -------------------------------------------------------------------------
    # Referencia al archivo en Supabase Storage
    # Path dentro del bucket: "transfers/{token}/{filename}"
    # -------------------------------------------------------------------------
    storage_path: Mapped[str] = mapped_column(String(500), nullable=False)

    # -------------------------------------------------------------------------
    # Fechas
    # -------------------------------------------------------------------------
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # -------------------------------------------------------------------------
    # Relación inversa con Transfer
    # -------------------------------------------------------------------------
    transfer: Mapped["Transfer"] = relationship(
        "Transfer",
        back_populates="files"
    )

    def __repr__(self) -> str:
        return f"<File {self.original_filename} ({self.mime_type}, {self.file_size} bytes)>"