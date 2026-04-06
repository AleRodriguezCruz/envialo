# =============================================================================
# security.py — Utilidades de seguridad
# Maneja: generación de tokens, validación de MIME, protección path traversal
# =============================================================================
import secrets
import uuid
import magic
from pathlib import Path

from app.core.config import settings


# -----------------------------------------------------------------------------
# GENERACIÓN DE TOKENS SEGUROS
# Combina UUID (único) + token aleatorio (impredecible)
# -----------------------------------------------------------------------------
def generate_transfer_token() -> str:
    """
    Genera un token seguro para identificar un transfer.
    Formato: UUID4 + 32 bytes aleatorios en hex
    Ejemplo: 550e8400-e29b-41d4-a716-446655440000-a3f8c2e1d4b7a9f0...
    """
    unique_id = str(uuid.uuid4())
    random_part = secrets.token_hex(32)
    return f"{unique_id}-{random_part}"


# -----------------------------------------------------------------------------
# VALIDACIÓN DE MIME CON MAGIC BYTES
# Lee los primeros bytes del archivo real, no confía en la extensión
# -----------------------------------------------------------------------------
def validate_mime_type(file_content: bytes) -> tuple[bool, str]:
    """
    Detecta el tipo MIME real del archivo usando magic bytes.
    Retorna: (es_valido, mime_type_detectado)
    """
    # Detecta el MIME leyendo los primeros bytes del archivo
    detected_mime = magic.from_buffer(file_content[:2048], mime=True)

    # Verifica si el MIME detectado está en la lista de permitidos
    is_valid = detected_mime in settings.ALLOWED_MIME_TYPES_LIST

    return is_valid, detected_mime


# -----------------------------------------------------------------------------
# VALIDACIÓN DE TAMAÑO
# -----------------------------------------------------------------------------
def validate_file_size(file_size: int) -> bool:
    """
    Verifica que el archivo no supere el tamaño máximo configurado.
    """
    return file_size <= settings.MAX_FILE_SIZE


# -----------------------------------------------------------------------------
# PROTECCIÓN CONTRA PATH TRAVERSAL
# Evita que nombres como "../../etc/passwd" escapen del directorio permitido
# -----------------------------------------------------------------------------
def sanitize_filename(filename: str) -> str:
    """
    Limpia el nombre del archivo para prevenir path traversal.
    - Elimina directorios (solo conserva el nombre base)
    - Reemplaza caracteres peligrosos
    - Limita la longitud
    """
    # Extrae solo el nombre base, ignorando cualquier ruta
    safe_name = Path(filename).name

    # Reemplaza caracteres peligrosos por guion bajo
    dangerous_chars = ['/', '\\', '..', '<', '>', ':', '"', '|', '?', '*']
    for char in dangerous_chars:
        safe_name = safe_name.replace(char, '_')

    # Limita el nombre a 255 caracteres (límite de la mayoría de sistemas)
    safe_name = safe_name[:255]

    # Si quedó vacío, usa un nombre genérico
    if not safe_name or safe_name.strip() == '':
        safe_name = 'archivo_sin_nombre'

    return safe_name


# -----------------------------------------------------------------------------
# BLOQUEO DE SCRIPTS EJECUTABLES
# Lista de extensiones peligrosas que nunca se permiten
# -----------------------------------------------------------------------------
BLOCKED_EXTENSIONS = {
    '.exe', '.bat', '.cmd', '.sh', '.ps1', '.vbs', '.js',
    '.jar', '.py', '.rb', '.php', '.pl', '.com', '.scr',
    '.msi', '.dll', '.so', '.dylib'
}


def is_executable_file(filename: str) -> bool:
    """
    Verifica si el archivo tiene una extensión ejecutable bloqueada.
    Retorna True si el archivo ES peligroso (debe bloquearse).
    """
    extension = Path(filename).suffix.lower()
    return extension in BLOCKED_EXTENSIONS