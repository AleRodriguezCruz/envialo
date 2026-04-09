# =============================================================================
# test_cleanup_worker.py — Tests del worker de limpieza
# =============================================================================
import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, patch

from app.workers.cleanup_worker import cleanup_expired_transfers
from app.db.models.transfer import Transfer
from app.db.models.file import File


# -----------------------------------------------------------------------------
# Test: el worker no falla cuando no hay transfers expirados
# -----------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_cleanup_no_expired_transfers():
    with patch(
        "app.workers.cleanup_worker.TransferRepository"
    ) as MockRepo:
        mock_repo = MockRepo.return_value
        mock_repo.get_expired_active = AsyncMock(return_value=[])

        # No debe lanzar ninguna excepción
        await cleanup_expired_transfers()


# -----------------------------------------------------------------------------
# Test: el worker procesa correctamente transfers expirados
# -----------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_cleanup_processes_expired_transfers():
    # Crea un transfer expirado de prueba
    mock_transfer = Transfer(
        id=1,
        token="test-token-expirado",
        is_active=True,
        expires_at=datetime.now(timezone.utc) - timedelta(hours=1),
        files=[]
    )

    with patch("app.workers.cleanup_worker.TransferRepository") as MockRepo, \
         patch("app.workers.cleanup_worker.StorageService") as MockStorage, \
         patch("app.workers.cleanup_worker.AuditService") as MockAudit:

        mock_repo = MockRepo.return_value
        mock_repo.get_expired_active = AsyncMock(return_value=[mock_transfer])
        mock_repo.mark_as_deleted = AsyncMock(return_value=True)

        mock_storage = MockStorage.return_value
        mock_storage.delete_transfer_files = AsyncMock(return_value=True)

        mock_audit = MockAudit.return_value
        mock_audit.log_expired = AsyncMock()

        await cleanup_expired_transfers()

        # Verifica que se intentó marcar como eliminado
        mock_repo.mark_as_deleted.assert_called_once_with("test-token-expirado")