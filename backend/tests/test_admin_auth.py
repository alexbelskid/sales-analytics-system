import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
import os

# Set environment for testing
os.environ["ADMIN_SECRET_KEY"] = "test-secret-key"

from app.main import app
from app.config import get_settings, Settings

client = TestClient(app)

# Override settings dependency to ensure we have the test key
def get_test_settings():
    s = Settings()
    s.admin_secret_key = "test-secret-key"
    return s

app.dependency_overrides[get_settings] = get_test_settings

def test_delete_all_data_protection():
    """
    Test that the destructive endpoint is protected.
    """
    with patch('app.routers.files_router.supabase') as mock_supa, \
         patch('app.database.get_supabase_admin') as mock_admin_getter, \
         patch('app.routers.files_router.delete_all_sales_data') as mock_endpoint:

        mock_admin = MagicMock()
        mock_admin_getter.return_value = mock_admin

        # 1. Missing Header -> 422 (FastAPI validation)
        response = client.delete("/api/files/delete-all-data")
        assert response.status_code == 422, f"Expected 422 for missing header, got {response.status_code}"

        # 2. Wrong Header -> 403 (Our check)
        response = client.delete("/api/files/delete-all-data", headers={"X-Admin-Key": "wrong-key"})
        assert response.status_code == 403, f"Expected 403 for wrong key, got {response.status_code}"

        # 3. Correct Header -> 200 (Success)
        # We need to mock the implementation to return success
        # But wait, if we mock delete_all_sales_data, we replace the whole function including dependency?
        # No, dependencies run before.
        # But patching `app.routers.files_router.delete_all_sales_data` replaces the decorated function?
        # Yes, usually.

        # Instead of patching the endpoint, let's just let it run but with mocked DB calls.
        # We already mocked DB calls in the `with` block above.

        # Reset mocks
        mock_admin.rpc.return_value.execute.return_value = MagicMock()

        response = client.delete("/api/files/delete-all-data", headers={"X-Admin-Key": "test-secret-key"})
        assert response.status_code == 200, f"Expected 200 for correct key, got {response.status_code}"
        assert response.json()["success"] is True

def test_delete_file_protection():
    """Test protection on single file deletion"""
    with patch('app.routers.files_router.supabase') as mock_supa:
        # Mock the select query to return a fake file
        mock_supa.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [{
            "id": "some-uuid",
            "import_source": "excel",
            "import_type": "sales",
            "storage_path": "path/to/file",
            "filename": "test.xlsx"
        }]

        # 1. Missing Header
        response = client.delete("/api/files/some-uuid")
        assert response.status_code == 422

        # 2. Wrong Header
        response = client.delete("/api/files/some-uuid", headers={"X-Admin-Key": "wrong"})
        assert response.status_code == 403

        # 3. Correct Header
        response = client.delete("/api/files/some-uuid", headers={"X-Admin-Key": "test-secret-key"})
        assert response.status_code == 200
        assert response.json()["success"] is True
