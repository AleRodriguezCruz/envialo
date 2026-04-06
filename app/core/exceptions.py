# =============================================================================
# exceptions.py — Excepciones personalizadas de la aplicación
# Cada excepción mapea a un código HTTP específico
# =============================================================================
from fastapi import HTTPException, status


# -----------------------------------------------------------------------------
# 404 — Recurso no encontrado
# Se lanza cuando el token no existe en la base de datos
# -----------------------------------------------------------------------------
class TransferNotFoundException(HTTPException):
    def __init__(self, token: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transfer con token '{token}' no encontrado."
        )


# -----------------------------------------------------------------------------
# 410 — Recurso eliminado o expirado
# Se lanza cuando el transfer existió pero ya expiró o fue eliminado
# -----------------------------------------------------------------------------
class TransferExpiredException(HTTPException):
    def __init__(self, token: str):
        super().__init__(
            status_code=status.HTTP_410_GONE,
            detail=f"El transfer '{token}' ha expirado o fue eliminado."
        )


# -----------------------------------------------------------------------------
# 413 — Archivo demasiado grande
# Se lanza cuando el archivo supera MAX_FILE_SIZE
# -----------------------------------------------------------------------------
class FileTooLargeException(HTTPException):
    def __init__(self, max_size_mb: int):
        super().__init__(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"El archivo supera el tamaño máximo permitido de {max_size_mb} MB."
        )


# -----------------------------------------------------------------------------
# 415 — Tipo de archivo no soportado
# Se lanza cuando el MIME detectado no está en la lista de permitidos
# -----------------------------------------------------------------------------
class UnsupportedFileTypeException(HTTPException):
    def __init__(self, detected_mime: str):
        super().__init__(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Tipo de archivo '{detected_mime}' no está permitido."
        )


# -----------------------------------------------------------------------------
# 400 — Archivo ejecutable bloqueado
# Se lanza cuando se intenta subir un script o ejecutable
# -----------------------------------------------------------------------------
class ExecutableFileException(HTTPException):
    def __init__(self, filename: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El archivo '{filename}' es un ejecutable y no está permitido."
        )


# -----------------------------------------------------------------------------
# 500 — Error interno de almacenamiento
# Se lanza cuando falla la comunicación con Supabase Storage
# -----------------------------------------------------------------------------
class StorageException(HTTPException):
    def __init__(self, detail: str = "Error al comunicarse con el almacenamiento."):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )