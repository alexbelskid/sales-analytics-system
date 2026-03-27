import pytest
from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch, MagicMock

client = TestClient(app)

@pytest.fixture
def mock_settings():
    with patch('app.dependencies.settings') as mock:
        mock.admin_secret_key = "secret-123"
        yield mock

@pytest.fixture
def mock_supabase():
    with patch('app.routers.files_router.supabase') as mock:
        mock.table.return_value = mock
        mock.select.return_value = mock
        mock.eq.return_value = mock
        mock.delete.return_value = mock
        mock.neq.return_value = mock
        mock.execute.return_value = MagicMock(data=[])

        # Mock storage
        mock.storage = MagicMock()
        mock.storage.from_.return_value = MagicMock()

        yield mock

def test_delete_all_sales_data_no_auth(mock_settings):
    """Test that endpoint returns 422 without auth header"""
    response = client.delete("/api/files/delete-all-data")
    assert response.status_code == 422 # Missing header

def test_delete_all_sales_data_wrong_key(mock_settings):
    """Test that endpoint returns 401 with wrong key"""
    response = client.delete(
        "/api/files/delete-all-data",
        headers={"X-Admin-Key": "wrong-key"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid Admin Key"

def test_delete_all_sales_data_success(mock_settings, mock_supabase):
    """Test that endpoint works with correct key"""
    # We need to mock get_supabase_admin in the module where it is defined
    with patch('app.database.get_supabase_admin', return_value=mock_supabase):
        # And cache
        with patch('app.services.cache_service.cache') as mock_cache:
            # Also patch settings inside files_router if used (it imports settings inside function)
            # Actually, files_router imports settings inside the function too:
            # from app.config import settings
            # So we should patch app.config.settings, but we already have mock_settings which patches app.dependencies.settings
            # We need to patch app.config.settings globally or patch where it is used.
            # Since files_router imports it inside the function, it pulls from app.config.
            with patch('app.config.settings') as config_settings:
                 config_settings.storage_bucket = "test-bucket"
                 config_settings.admin_secret_key = "secret-123" # Must match verify_admin_access if used there (but verify uses dependency)

                 response = client.delete(
                    "/api/files/delete-all-data",
                    headers={"X-Admin-Key": "secret-123"}
                )
                 assert response.status_code == 200
                 assert response.json()["success"] == True

def test_delete_file_auth(mock_settings, mock_supabase):
    """Test auth for delete_file endpoint"""
    file_id = "test-id"

    # 1. Fail without key
    response = client.delete(f"/api/files/{file_id}")
    assert response.status_code == 422

    # 2. Fail with wrong key
    response = client.delete(
        f"/api/files/{file_id}",
        headers={"X-Admin-Key": "wrong"}
    )
    assert response.status_code == 401

    # 3. Success with key (mocking DB response)
    mock_supabase.select.return_value.eq.return_value.execute.return_value.data = [{
        "id": file_id, "filename": "test.csv"
    }]

    with patch('app.services.cache_service.cache') as mock_cache:
         response = client.delete(
            f"/api/files/{file_id}",
            headers={"X-Admin-Key": "secret-123"}
        )
         assert response.status_code == 200

def test_server_misconfiguration():
    """Test that endpoint returns 500 if admin key is not set"""
    # We explicitly mock settings to have empty key
    with patch('app.dependencies.settings') as mock:
        mock.admin_secret_key = ""

        response = client.delete(
            "/api/files/delete-all-data",
            headers={"X-Admin-Key": "any-key"}
        )
        assert response.status_code == 500
        assert "Server misconfiguration" in response.json()["detail"]

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
