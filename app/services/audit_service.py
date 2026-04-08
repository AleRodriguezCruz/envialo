# =============================================================================
# audit_service.py — Servicio de auditoría
# Responsabilidad: registrar cada acción importante en la tabla audit_logs
# de Supabase (upload, download, delete, expired, error)
# =============================================================================
from app.db.supabase import supabase_service


class AuditService:

    def __init__(self):
        # Usa el cliente service_role para escribir en audit_logs
        self.client = supabase_service

    # -------------------------------------------------------------------------
    # REGISTRAR una acción en audit_logs
    # -------------------------------------------------------------------------
    async def log(
        self,
        transfer_token: str,
        action: str,
        metadata: dict | None = None,
        ip_address: str | None = None
    ) -> None:
        try:
            self.client.table("audit_logs").insert({
                "transfer_token": transfer_token,
                "action": action,
                "metadata": metadata or {},
                "ip_address": ip_address
            }).execute()
        except Exception as e:
            # Los errores de auditoría no deben interrumpir el flujo principal
            print(f"[AuditService] Error al registrar log: {str(e)}")

    # -------------------------------------------------------------------------
    # Métodos de conveniencia para cada tipo de acción
    # -------------------------------------------------------------------------
    async def log_upload(self, token: str, filename: str, ip: str | None = None):
        await self.log(
            transfer_token=token,
            action="upload",
            metadata={"filename": filename},
            ip_address=ip
        )

    async def log_download(self, token: str, filename: str, ip: str | None = None):
        await self.log(
            transfer_token=token,
            action="download",
            metadata={"filename": filename},
            ip_address=ip
        )

    async def log_delete(self, token: str, ip: str | None = None):
        await self.log(
            transfer_token=token,
            action="delete",
            ip_address=ip
        )

    async def log_expired(self, token: str):
        await self.log(
            transfer_token=token,
            action="expired",
            metadata={"reason": "automatic cleanup"}
        )

    async def log_error(self, token: str, error: str, ip: str | None = None):
        await self.log(
            transfer_token=token,
            action="error",
            metadata={"error": error},
            ip_address=ip
        )


# Instancia global del servicio
audit_service = AuditService()# =============================================================================
# audit_service.py — Servicio de auditoría
# Responsabilidad: registrar cada acción importante en la tabla audit_logs
# de Supabase (upload, download, delete, expired, error)
# =============================================================================
from app.db.supabase import supabase_service


class AuditService:

    def __init__(self):
        # Usa el cliente service_role para escribir en audit_logs
        self.client = supabase_service

    # -------------------------------------------------------------------------
    # REGISTRAR una acción en audit_logs
    # -------------------------------------------------------------------------
    async def log(
        self,
        transfer_token: str,
        action: str,
        metadata: dict | None = None,
        ip_address: str | None = None
    ) -> None:
        try:
            self.client.table("audit_logs").insert({
                "transfer_token": transfer_token,
                "action": action,
                "metadata": metadata or {},
                "ip_address": ip_address
            }).execute()
        except Exception as e:
            # Los errores de auditoría no deben interrumpir el flujo principal
            print(f"[AuditService] Error al registrar log: {str(e)}")

    # -------------------------------------------------------------------------
    # Métodos de conveniencia para cada tipo de acción
    # -------------------------------------------------------------------------
    async def log_upload(self, token: str, filename: str, ip: str | None = None):
        await self.log(
            transfer_token=token,
            action="upload",
            metadata={"filename": filename},
            ip_address=ip
        )

    async def log_download(self, token: str, filename: str, ip: str | None = None):
        await self.log(
            transfer_token=token,
            action="download",
            metadata={"filename": filename},
            ip_address=ip
        )

    async def log_delete(self, token: str, ip: str | None = None):
        await self.log(
            transfer_token=token,
            action="delete",
            ip_address=ip
        )

    async def log_expired(self, token: str):
        await self.log(
            transfer_token=token,
            action="expired",
            metadata={"reason": "automatic cleanup"}
        )

    async def log_error(self, token: str, error: str, ip: str | None = None):
        await self.log(
            transfer_token=token,
            action="error",
            metadata={"error": error},
            ip_address=ip
        )


# Instancia global del servicio
audit_service = AuditService()