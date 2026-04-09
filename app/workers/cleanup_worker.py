# =============================================================================
# cleanup_worker.py — Worker de limpieza automática
# Responsabilidad: cada N horas busca transfers expirados,
# elimina sus archivos de Supabase Storage y los marca en PostgreSQL
# =============================================================================
import logging
from datetime import datetime, timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.postgres import AsyncSessionLocal
from app.repositories.transfer_repo import TransferRepository
from app.services.storage_service import StorageService
from app.services.audit_service import AuditService

# Configura el logger para el worker
logger = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# TAREA PRINCIPAL DE LIMPIEZA
# Se ejecuta automáticamente cada CLEANUP_INTERVAL_HOURS horas
# -----------------------------------------------------------------------------
async def cleanup_expired_transfers() -> None:
    logger.info(f"[Worker] Iniciando limpieza de transfers expirados...")

    # Crea una sesión de DB específica para el worker
    async with AsyncSessionLocal() as db:
        try:
            transfer_repo = TransferRepository(db)
            storage = StorageService()
            audit = AuditService()

            # Busca todos los transfers activos que ya expiraron
            expired_transfers = await transfer_repo.get_expired_active()

            if not expired_transfers:
                logger.info("[Worker] No hay transfers expirados. Nada que limpiar.")
                return

            logger.info(f"[Worker] Encontrados {len(expired_transfers)} transfers expirados.")

            # Procesa cada transfer expirado
            cleaned_count = 0
            for transfer in expired_transfers:
                try:
                    # Obtiene las rutas de los archivos en Supabase Storage
                    storage_paths = [f.storage_path for f in transfer.files]

                    # Elimina los archivos de Supabase Storage
                    if storage_paths:
                        await storage.delete_transfer_files(storage_paths)
                        logger.info(
                            f"[Worker] Eliminados {len(storage_paths)} archivos "
                            f"del transfer {transfer.token[:20]}..."
                        )

                    # Marca el transfer como expirado en PostgreSQL
                    await transfer_repo.mark_as_deleted(transfer.token)

                    # Registra el evento en audit_logs
                    await audit.log_expired(token=transfer.token)

                    cleaned_count += 1

                except Exception as e:
                    logger.error(
                        f"[Worker] Error procesando transfer {transfer.token[:20]}: {str(e)}"
                    )
                    continue

            # Confirma todos los cambios en PostgreSQL
            await db.commit()
            logger.info(f"[Worker] Limpieza completada. {cleaned_count} transfers eliminados.")

        except Exception as e:
            await db.rollback()
            logger.error(f"[Worker] Error general en limpieza: {str(e)}")


# -----------------------------------------------------------------------------
# CONFIGURACIÓN DEL SCHEDULER
# Usa APScheduler con el event loop de FastAPI (AsyncIOScheduler)
# -----------------------------------------------------------------------------
def create_scheduler() -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler()

    # Agrega el job de limpieza con intervalo configurable desde .env
    scheduler.add_job(
        cleanup_expired_transfers,
        trigger="interval",
        hours=settings.CLEANUP_INTERVAL_HOURS,
        id="cleanup_expired_transfers",
        name="Limpieza de transfers expirados",
        replace_existing=True
    )

    logger.info(
        f"[Worker] Scheduler configurado: limpieza cada "
        f"{settings.CLEANUP_INTERVAL_HOURS} horas."
    )

    return scheduler