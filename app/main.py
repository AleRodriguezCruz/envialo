# =============================================================================
# main.py — Punto de entrada de la aplicación FastAPI
# Configura: CORS, rutas, lifespan (inicio y cierre de recursos)
# =============================================================================
import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.core.config import settings
from app.api.v1.router import api_router
from app.workers.cleanup_worker import create_scheduler

# Configura el logger principal
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
)
logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# RUTAS DE ARCHIVOS (Compatibilidad con Docker/Railway)
# -----------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Si tu carpeta 'frontend' está en la raíz del proyecto:
FRONTEND_DIR = os.path.join(os.getcwd(), "frontend")

# -----------------------------------------------------------------------------
# LIFESPAN — Maneja el ciclo de vida de la aplicación
# -----------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    # ----- INICIO -----
    logger.info("🚀 Iniciando aplicación Envialo...")

    # Inicia el scheduler del worker de limpieza
    try:
        scheduler = create_scheduler()
        scheduler.start()
        logger.info("✅ Worker de limpieza iniciado correctamente.")
    except Exception as e:
        logger.error(f"❌ Error al iniciar el worker de limpieza: {e}")
        scheduler = None

    yield  # La app corre aquí

    # ----- CIERRE -----
    if scheduler:
        logger.info("Stopping aplicación Envialo...")
        scheduler.shutdown()
        logger.info("✅ Worker de limpieza detenido.")


# -----------------------------------------------------------------------------
# INSTANCIA DE FASTAPI
# -----------------------------------------------------------------------------
app = FastAPI(
    title="Envialo",
    description="Clon de WeTransfer con FastAPI, PostgreSQL y Supabase",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)


# -----------------------------------------------------------------------------
# CORS — Permite peticiones desde el frontend
# -----------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------------------------------------------------------
# FRONTEND — Sirve los archivos estáticos y el index.html
# -----------------------------------------------------------------------------
# Verificamos si la carpeta existe antes de montar para evitar que la app explote
if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")
    logger.info(f"📁 Carpeta frontend montada desde: {FRONTEND_DIR}")
else:
    logger.warning(f"⚠️ Alerta: No se encontró la carpeta frontend en {FRONTEND_DIR}")


@app.get("/", include_in_schema=False)
async def serve_frontend():
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {
        "error": "Frontend no encontrado", 
        "path_searched": index_path,
        "current_dir": os.getcwd()
    }


# -----------------------------------------------------------------------------
# RUTAS DE LA API
# -----------------------------------------------------------------------------
app.include_router(api_router)


# -----------------------------------------------------------------------------
# RUTA DE SALUD (Crítica para Railway)
# -----------------------------------------------------------------------------
@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "ok",
        "app": "Envialo",
        "version": "0.1.0",
        "environment": settings.APP_ENV,
        "database": "connected" # Podrías agregar un check real de DB aquí
    }