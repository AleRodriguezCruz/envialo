# =============================================================================
# test_upload.py — Tests del endpoint POST /upload
# =============================================================================
import pytest
from httpx import AsyncClient


# -----------------------------------------------------------------------------
# Test: subida exitosa de un archivo PNG válido
# -----------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_upload_valid_file(client: AsyncClient, sample_png_file: bytes):
    response = await client.post(
        "/api/v1/upload",
        files={"file": ("test.png", sample_png_file, "image/png")},
        data={"message": "Hola desde el test"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    assert "download_url" in data
    assert data["filename"] == "test.png"
    assert data["mime_type"] == "image/png"


# -----------------------------------------------------------------------------
# Test: rechazo de archivo ejecutable (.exe)
# -----------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_upload_executable_file(client: AsyncClient):
    fake_exe = b"MZ\x90\x00"  # Magic bytes de un ejecutable Windows
    response = await client.post(
        "/api/v1/upload",
        files={"file": ("virus.exe", fake_exe, "application/octet-stream")}
    )
    assert response.status_code == 400


# -----------------------------------------------------------------------------
# Test: rechazo de archivo demasiado grande
# -----------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_upload_file_too_large(client: AsyncClient):
    # Crea un archivo que supera MAX_FILE_SIZE
    large_file = b"x" * (104857600 + 1)  # 100MB + 1 byte
    response = await client.post(
        "/api/v1/upload",
        files={"file": ("large.png", large_file, "image/png")}
    )
    assert response.status_code == 413


# -----------------------------------------------------------------------------
# Test: rechazo de tipo MIME no permitido
# -----------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_upload_invalid_mime(client: AsyncClient):
    # Archivo con magic bytes de ejecutable pero extensión .png
    fake_file = b"MZ\x90\x00\x03\x00\x00\x00"
    response = await client.post(
        "/api/v1/upload",
        files={"file": ("fake.png", fake_file, "image/png")}
    )
    assert response.status_code == 415