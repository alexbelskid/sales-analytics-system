import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import sys
import os

# Ensure backend is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import app

# Create client
client = TestClient(app)

@pytest.fixture
def mock_supabase():
    # Mock the internal import in delete_all_sales_data
    with patch("app.database.get_supabase_admin") as mock_admin, \
         patch("app.routers.files_router.supabase") as mock_router_supabase:

        mock_db = MagicMock()
        mock_admin.return_value = mock_db
        mock_router_supabase.table.return_value = mock_db.table.return_value

        # Mock chain for delete/execute to return success
        # For delete_all_sales_data (complex)
        mock_db.rpc.return_value.execute.return_value = MagicMock(data=[])

        # For delete_all_sales (simple)
        mock_db.table.return_value.select.return_value.execute.return_value = MagicMock(count=10)
        mock_db.table.return_value.delete.return_value.neq.return_value.execute.return_value = MagicMock(data=[])

        yield mock_db

def test_delete_all_security_no_key_dev(mock_supabase):
    """
    Test that in development with no key, access is ALLOWED.
    """
    with patch("app.dependencies.settings.admin_secret_key", None), \
         patch("app.dependencies.settings.environment", "development"):

        # Test complex delete
        response = client.delete("/api/files/delete-all-data")
        assert response.status_code == 200

        # Test simple delete
        response = client.delete("/api/files/all-sales")
        assert response.status_code == 200

def test_delete_all_security_no_key_prod(mock_supabase):
    """
    Test that in production with no key, access is BLOCKED.
    """
    with patch("app.dependencies.settings.admin_secret_key", None), \
         patch("app.dependencies.settings.environment", "production"):

        response = client.delete("/api/files/delete-all-data")
        assert response.status_code == 403
        assert "not configured in production" in response.json()["detail"]

def test_delete_all_security_with_key_success(mock_supabase):
    """
    Test that with key configured and provided, access is ALLOWED.
    """
    with patch("app.dependencies.settings.admin_secret_key", "secret123"), \
         patch("app.dependencies.settings.environment", "production"):

        response = client.delete(
            "/api/files/delete-all-data",
            headers={"X-Admin-Key": "secret123"}
        )
        assert response.status_code == 200

def test_delete_all_security_with_key_fail(mock_supabase):
    """
    Test that with key configured but NOT provided (or wrong), access is BLOCKED.
    """
    with patch("app.dependencies.settings.admin_secret_key", "secret123"):

        # No header
        response = client.delete("/api/files/delete-all-data")
        assert response.status_code == 403

        # Wrong header
        response = client.delete(
            "/api/files/delete-all-data",
            headers={"X-Admin-Key": "wrong"}
        )
        assert response.status_code == 403
