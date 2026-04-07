# =============================================================================
# env.py — Configuración de Alembic para migraciones
# Usa psycopg2 (sync) para conectarse, que es lo que Alembic necesita
# =============================================================================
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# Importa la configuración de la app
from app.core.config import settings

# Importa la Base y los modelos para que Alembic los detecte
from app.db.postgres import Base
from app.db.models.transfer import Transfer  # noqa: F401
from app.db.models.file import File          # noqa: F401

# Configuración de logging
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata de los modelos
target_metadata = Base.metadata

# Sobreescribe la URL usando psycopg2 (sync) en lugar de asyncpg
config.set_main_option(
    "sqlalchemy.url",
    settings.DATABASE_URL.replace("postgresql+asyncpg", "postgresql+psycopg2")
)


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()