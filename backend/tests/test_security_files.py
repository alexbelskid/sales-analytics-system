import pytest
from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch, MagicMock

client = TestClient(app)

@pytest.fixture
def mock_admin_key():
    # We need to set a key so the server doesn't 500
    with patch("app.dependencies.settings.admin_secret_key", "test-secret-key"):
        yield "test-secret-key"

def test_delete_all_data_unauthorized(mock_admin_key):
    """Test that endpoint returns 401/403 without key."""
    with patch("app.database.get_supabase_admin"):
        response = client.delete("/api/files/delete-all-data")
        assert response.status_code in [401, 403]

def test_delete_all_data_authorized(mock_admin_key):
    """Test that endpoint works with correct key."""
    with patch("app.database.get_supabase_admin") as mock_get_admin:
        mock_client = MagicMock()
        mock_get_admin.return_value = mock_client
        mock_client.table.return_value.select.return_value.execute.return_value.data = []
        mock_client.rpc.return_value.execute.return_value = None
        mock_client.storage.from_.return_value.remove.return_value = []

        with patch("app.services.cache_service.cache.invalidate_pattern"), \
             patch("app.services.cache_service.cache.clear"):

            response = client.delete(
                "/api/files/delete-all-data",
                headers={"X-Admin-Key": mock_admin_key}
            )
            assert response.status_code == 200

def test_delete_file_unauthorized(mock_admin_key):
    """Test that deleting a file requires auth."""
    # Even if we mock everything else, it should fail auth first
    response = client.delete("/api/files/test-id")
    assert response.status_code in [401, 403]

def test_delete_file_authorized(mock_admin_key):
    """Test that deleting a file works with auth."""
    with patch("app.routers.files_router.supabase") as mock_supabase:
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
            {"id": "test-id", "filename": "test.xlsx", "import_source": "excel_upload", "import_type": "sales", "storage_path": "path/to/file"}
        ]

        mock_result = MagicMock()
        mock_result.data = []
        mock_supabase.table.return_value.delete.return_value.eq.return_value.execute.return_value = mock_result
        mock_supabase.table.return_value.delete.return_value.in_.return_value.execute.return_value = mock_result
        mock_supabase.storage.from_.return_value.remove.return_value = {}

        with patch("app.services.cache_service.cache.invalidate_pattern"), \
             patch("app.services.cache_service.cache.invalidate_all_agent_cache"), \
             patch("app.services.cache_service.cache.clear"), \
             patch("app.services.cache_service.cache.get_stats", return_value={'total_entries': 0, 'keys': []}):

            response = client.delete(
                "/api/files/test-id",
                headers={"X-Admin-Key": mock_admin_key}
            )
            assert response.status_code == 200

def test_delete_file_wrong_key(mock_admin_key):
    """Test that incorrect key fails."""
    response = client.delete(
        "/api/files/test-id",
        headers={"X-Admin-Key": "wrong-key"}
    )
    assert response.status_code == 403
