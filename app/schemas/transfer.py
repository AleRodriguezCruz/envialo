# =============================================================================
# transfer.py — Schemas de Pydantic para validación de datos
# Define la estructura de los datos de entrada y salida de la API
# =============================================================================
from datetime import datetime
from pydantic import BaseModel


# -----------------------------------------------------------------------------
# RESPUESTA de subida exitosa
# -----------------------------------------------------------------------------
class UploadResponse(BaseModel):
    token: str
    filename: str
    mime_type: str
    file_size: int
    expires_at: str
    download_url: str


# -----------------------------------------------------------------------------
# INFORMACIÓN de un archivo individual
# -----------------------------------------------------------------------------
class FileInfo(BaseModel):
    id: int
    filename: str
    mime_type: str
    file_size: int


# -----------------------------------------------------------------------------
# INFORMACIÓN pública de un transfer
# -----------------------------------------------------------------------------
class TransferInfo(BaseModel):
    token: str
    message: str | None
    expires_at: str
    download_count: int
    files: list[FileInfo]


# -----------------------------------------------------------------------------
# RESPUESTA de descarga con URLs firmadas
# -----------------------------------------------------------------------------
class DownloadInfo(BaseModel):
    filename: str
    mime_type: str
    file_size: int
    download_url: str


# -----------------------------------------------------------------------------
# RESPUESTA de eliminación
# -----------------------------------------------------------------------------
class DeleteResponse(BaseModel):
    message: str