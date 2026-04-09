# =============================================================================
# test_download.py — Tests de los endpoints de descarga y eliminación
# =============================================================================
import pytest
from httpx import AsyncClient


# -----------------------------------------------------------------------------
# Test: token inexistente retorna 404
# -----------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_download_nonexistent_token(client: AsyncClient):
    response = await client.get("/api/v1/download/token-que-no-existe")
    assert response.status_code == 404


# -----------------------------------------------------------------------------
# Test: obtener info de transfer inexistente retorna 404
# -----------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_get_file_info_nonexistent(client: AsyncClient):
    response = await client.get("/api/v1/file/token-que-no-existe")
    assert response.status_code == 404


# -----------------------------------------------------------------------------
# Test: eliminar transfer inexistente retorna 404
# -----------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_delete_nonexistent_token(client: AsyncClient):
    response = await client.delete("/api/v1/file/token-que-no-existe")
    assert response.status_code == 404


# -----------------------------------------------------------------------------
# Test: flujo completo — subir y luego obtener info
# -----------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_upload_then_get_info(client: AsyncClient, sample_png_file: bytes):
    # Sube el archivo
    upload_response = await client.post(
        "/api/v1/upload",
        files={"file": ("test.png", sample_png_file, "image/png")}
    )
    assert upload_response.status_code == 200
    token = upload_response.json()["token"]

    # Obtiene la info del transfer
    info_response = await client.get(f"/api/v1/file/{token}")
    assert info_response.status_code == 200
    data = info_response.json()
    assert data["token"] == token
    assert len(data["files"]) == 1
    assert data["files"][0]["filename"] == "test.png"