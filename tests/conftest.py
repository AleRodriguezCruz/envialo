# =============================================================================
# conftest.py — Configuración global de tests
# Define fixtures compartidas: cliente de prueba, DB de prueba, etc.
# =============================================================================
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.main import app
from app.db.postgres import Base, get_db
from app.core.config import settings

# URL de la DB de prueba — usa la misma PostgreSQL pero una DB separada
TEST_DATABASE_URL = settings.DATABASE_URL.replace(
    settings.POSTGRES_DB, f"{settings.POSTGRES_DB}_test"
)

# Motor de DB para tests
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False
)


# -----------------------------------------------------------------------------
# Fixture: crea y destruye las tablas de test antes/después de cada sesión
# -----------------------------------------------------------------------------
@pytest.fixture(scope="session", autouse=True)
async def setup_test_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# -----------------------------------------------------------------------------
# Fixture: sesión de DB de prueba por cada test
# -----------------------------------------------------------------------------
@pytest.fixture
async def db_session():
    async with TestSessionLocal() as session:
        yield session
        await session.rollback()


# -----------------------------------------------------------------------------
# Fixture: cliente HTTP de prueba
# Sobreescribe la dependencia get_db con la DB de prueba
# -----------------------------------------------------------------------------
@pytest.fixture
async def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


# -----------------------------------------------------------------------------
# Fixture: archivo de prueba en memoria (imagen PNG pequeña válida)
# -----------------------------------------------------------------------------
@pytest.fixture
def sample_png_file():
    # PNG mínimo válido de 1x1 pixel
    png_bytes = (
        b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01'
        b'\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00'
        b'\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18'
        b'\xd8N\x00\x00\x00\x00IEND\xaeB`\x82'
    )
    return png_bytes