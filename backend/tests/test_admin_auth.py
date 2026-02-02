import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.config import settings
from unittest.mock import patch, MagicMock

client = TestClient(app)

# Use a test key
TEST_ADMIN_KEY = "test-secret-key-123"

@pytest.fixture
def mock_admin_settings():
    """Override settings to have a known admin key"""
    original_key = settings.admin_secret_key
    settings.admin_secret_key = TEST_ADMIN_KEY
    yield
    settings.admin_secret_key = original_key

@pytest.fixture
def mock_files_supabase():
    """Mock supabase in files_router specifically"""
    mock = MagicMock()
    # Mock return values to simulate success if auth passes
    mock.table.return_value.delete.return_value.neq.return_value.execute.return_value.data = []
    mock.table.return_value.update.return_value.execute.return_value.data = []
    mock.table.return_value.select.return_value.execute.return_value.data = []
    mock.rpc.return_value.execute.return_value.data = None

    # Patch the module-level supabase
    with patch("app.routers.files_router.supabase", mock):
        yield mock

def test_delete_all_sales_no_auth(mock_admin_settings):
    """Verify 401 when no auth header is provided"""
    response = client.delete("/api/files/delete-all-data")
    assert response.status_code == 401
    assert "Missing admin key" in response.json()["detail"]

def test_delete_all_sales_invalid_auth(mock_admin_settings):
    """Verify 401 when invalid auth header is provided"""
    response = client.delete(
        "/api/files/delete-all-data",
        headers={"X-Admin-Key": "wrong-key"}
    )
    assert response.status_code == 401
    assert "Invalid admin key" in response.json()["detail"]

def test_delete_all_sales_valid_auth(mock_admin_settings, mock_files_supabase):
    """Verify 200/Success when valid auth header is provided"""
    # We also need to mock get_supabase_admin which is imported inside the function
    # Because the function does: from app.database import get_supabase_admin
    # We patch app.database.get_supabase_admin
    with patch("app.database.get_supabase_admin", return_value=mock_files_supabase):
        response = client.delete(
            "/api/files/delete-all-data",
            headers={"X-Admin-Key": TEST_ADMIN_KEY}
        )

        # It might fail with other errors because of deep logic, but definitely NOT 401
        assert response.status_code != 401

        if response.status_code != 200:
            print(f"Response: {response.json()}")

        assert response.status_code == 200
        assert response.json()["success"] is True

def test_reset_stuck_auth(mock_admin_settings, mock_files_supabase):
    """Verify auth on another endpoint"""
    # No auth
    response = client.post("/api/files/reset-stuck")
    assert response.status_code == 401

    # Valid auth
    response = client.post(
        "/api/files/reset-stuck",
        headers={"X-Admin-Key": TEST_ADMIN_KEY}
    )
    assert response.status_code == 200

def test_admin_key_not_configured():
    """Verify 500 when admin key is not set in config"""
    original_key = settings.admin_secret_key
    settings.admin_secret_key = "" # Simulate missing config
    try:
        response = client.delete(
            "/api/files/delete-all-data",
            headers={"X-Admin-Key": "any-key"}
        )
        assert response.status_code == 500
        assert "Server configuration error" in response.json()["detail"]
    finally:
        settings.admin_secret_key = original_key
