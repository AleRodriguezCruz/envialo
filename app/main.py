# =============================================================================
# main.py — Punto de entrada de la aplicación FastAPI
# Configura: CORS, rutas, lifespan (inicio y cierre de recursos)
# =============================================================================
import logging
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
# LIFESPAN — Maneja el ciclo de vida de la aplicación
# Se ejecuta al iniciar y al cerrar la app
# -----------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    # ----- INICIO -----
    logger.info("Iniciando aplicación Envialo...")

    # Inicia el scheduler del worker de limpieza
    scheduler = create_scheduler()
    scheduler.start()
    logger.info("Worker de limpieza iniciado.")

    yield  # La app corre aquí

    # ----- CIERRE -----
    logger.info("Cerrando aplicación Envialo...")
    scheduler.shutdown()
    logger.info("Worker de limpieza detenido.")


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
app.mount("/static", StaticFiles(directory="frontend"), name="static")


@app.get("/", include_in_schema=False)
async def serve_frontend():
    return FileResponse("frontend/index.html")


# -----------------------------------------------------------------------------
# RUTAS DE LA API
# -----------------------------------------------------------------------------
app.include_router(api_router)


# -----------------------------------------------------------------------------
# RUTA DE SALUD
# -----------------------------------------------------------------------------
@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "ok",
        "app": "Envialo",
        "version": "0.1.0",
        "environment": settings.APP_ENV
    }