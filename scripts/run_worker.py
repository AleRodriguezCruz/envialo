# =============================================================================
# run_worker.py — Script para correr el worker manualmente
# Útil para probar la limpieza sin esperar el intervalo del scheduler
# Uso: python scripts/run_worker.py
# =============================================================================
import asyncio
import logging

# Configura logging para ver los mensajes del worker
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

from app.workers.cleanup_worker import cleanup_expired_transfers


async def main():
    print("=== Ejecutando limpieza manual de transfers expirados ===")
    await cleanup_expired_transfers()
    print("=== Limpieza completada ===")


if __name__ == "__main__":
    asyncio.run(main())