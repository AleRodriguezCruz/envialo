# =============================================================================
# supabase.py — Cliente de Supabase
# Provee dos clientes:
#   - client_anon: para operaciones públicas (no usado directamente en backend)
#   - client_service: para operaciones privilegiadas (Storage + audit_logs)
# =============================================================================
from supabase import create_client, Client

from app.core.config import settings


# -----------------------------------------------------------------------------
# Cliente con clave anon (permisos limitados por RLS)
# -----------------------------------------------------------------------------
def get_supabase_client() -> Client:
    """
    Retorna un cliente Supabase con la clave anon/public.
    Respeta las políticas de Row Level Security (RLS).
    """
    return create_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_ANON_KEY
    )


# -----------------------------------------------------------------------------
# Cliente con clave service_role (permisos elevados, bypasea RLS)
# SOLO usar en el backend, NUNCA exponer al frontend
# -----------------------------------------------------------------------------
def get_supabase_service_client() -> Client:
    """
    Retorna un cliente Supabase con la clave service_role.
    Tiene acceso completo a Storage y audit_logs sin restricciones de RLS.
    """
    return create_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_SERVICE_KEY
    )


# -----------------------------------------------------------------------------
# Instancias globales — se crean una sola vez al iniciar la app
# -----------------------------------------------------------------------------
supabase_client = get_supabase_client()
supabase_service = get_supabase_service_client()