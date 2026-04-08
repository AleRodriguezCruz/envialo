# =============================================================================
# storage_service.py — Servicio de almacenamiento en Supabase Storage
# Responsabilidad: subir, eliminar y generar URLs firmadas de archivos
# =============================================================================
from app.db.supabase import supabase_service
from app.core.config import settings
from app.core.exceptions import StorageException


class StorageService:

    def __init__(self):
        # Usa el cliente service_role para tener permisos completos
        self.client = supabase_service
        self.bucket = settings.SUPABASE_BUCKET

    # -------------------------------------------------------------------------
    # SUBIR archivo a Supabase Storage
    # storage_path: ruta dentro del bucket ej: "transfers/token123/archivo.pdf"
    # -------------------------------------------------------------------------
    async def upload_file(
        self,
        storage_path: str,
        file_content: bytes,
        mime_type: str
    ) -> str:
        try:
            # Sube el archivo al bucket de Supabase
            response = self.client.storage.from_(self.bucket).upload(
                path=storage_path,
                file=file_content,
                file_options={"content-type": mime_type}
            )
            return storage_path
        except Exception as e:
            raise StorageException(f"Error al subir archivo: {str(e)}")

    # -------------------------------------------------------------------------
    # ELIMINAR archivo de Supabase Storage
    # -------------------------------------------------------------------------
    async def delete_file(self, storage_path: str) -> bool:
        try:
            self.client.storage.from_(self.bucket).remove([storage_path])
            return True
        except Exception as e:
            raise StorageException(f"Error al eliminar archivo: {str(e)}")

    # -------------------------------------------------------------------------
    # ELIMINAR todos los archivos de un transfer
    # -------------------------------------------------------------------------
    async def delete_transfer_files(self, storage_paths: list[str]) -> bool:
        try:
            if storage_paths:
                self.client.storage.from_(self.bucket).remove(storage_paths)
            return True
        except Exception as e:
            raise StorageException(f"Error al eliminar archivos del transfer: {str(e)}")

    # -------------------------------------------------------------------------
    # GENERAR URL firmada para descarga segura
    # La URL expira después de N segundos (default: 1 hora)
    # -------------------------------------------------------------------------
    async def create_signed_url(
        self,
        storage_path: str,
        expires_in: int = 3600
    ) -> str:
        try:
            response = self.client.storage.from_(self.bucket).create_signed_url(
                path=storage_path,
                expires_in=expires_in
            )
            # La respuesta contiene la URL firmada
            if "signedURL" in response:
                return response["signedURL"]
            elif "signedUrl" in response:
                return response["signedUrl"]
            else:
                raise StorageException("No se pudo generar la URL firmada")
        except StorageException:
            raise
        except Exception as e:
            raise StorageException(f"Error al generar URL firmada: {str(e)}")


# Instancia global del servicio
storage_service = StorageService()