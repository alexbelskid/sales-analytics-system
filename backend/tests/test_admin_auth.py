import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.config import get_settings, Settings
from unittest.mock import MagicMock, patch

client = TestClient(app)

# Endpoints to test
DESTRUCTIVE_ENDPOINTS = [
    ("DELETE", "/api/files/delete-all-data"),
    ("DELETE", "/api/files/all-sales"),
    ("POST", "/api/files/reset-stuck"),
    ("DELETE", "/api/files/mock-id"), # file_id
    ("DELETE", "/api/files/sales-data/mock-id"),
]

def test_missing_header_returns_401():
    # Use dependency override to enforce a known admin key
    def get_settings_override():
        # Override values to ensure consistent test environment
        return Settings(admin_secret_key="secure-key")

    app.dependency_overrides[get_settings] = get_settings_override

    for method, url in DESTRUCTIVE_ENDPOINTS:
        response = client.request(method, url) # No headers
        assert response.status_code == 401, f"Endpoint {url} did not enforce auth (missing header)"
        assert response.json()["detail"] == "Missing admin key"

    app.dependency_overrides.clear()

def test_wrong_header_returns_401():
    def get_settings_override():
        return Settings(admin_secret_key="secure-key")

    app.dependency_overrides[get_settings] = get_settings_override

    for method, url in DESTRUCTIVE_ENDPOINTS:
        response = client.request(method, url, headers={"X-Admin-Key": "wrong-key"})
        assert response.status_code == 401, f"Endpoint {url} did not enforce auth (wrong key)"
        assert response.json()["detail"] == "Invalid admin key"

    app.dependency_overrides.clear()

def test_server_misconfiguration_returns_500():
    # Test when admin_secret_key is empty (default)
    def get_settings_override():
        # Create settings with empty key
        return Settings(admin_secret_key="")

    app.dependency_overrides[get_settings] = get_settings_override

    for method, url in DESTRUCTIVE_ENDPOINTS:
        # Even with a key provided by client, server should fail if not configured
        response = client.request(method, url, headers={"X-Admin-Key": "some-key"})
        assert response.status_code == 500, f"Endpoint {url} did not fail securely when unconfigured"
        assert "Server administration is not configured" in response.json()["detail"]

    app.dependency_overrides.clear()

def test_correct_header_passes_auth():
    # Verify that valid credentials allow access to the business logic
    def get_settings_override():
        return Settings(admin_secret_key="secure-key")

    app.dependency_overrides[get_settings] = get_settings_override

    # Patch supabase in files_router to ensure it returns data properly for the chain
    # reset-stuck uses: supabase.table().select().eq().lt().execute()
    with patch("app.routers.files_router.supabase") as mock_db:
        # Mock the select chain
        mock_db.table.return_value.select.return_value.eq.return_value.lt.return_value.execute.return_value.data = []

        # Test one endpoint completely to verify auth pass-through
        response = client.post("/api/files/reset-stuck", headers={"X-Admin-Key": "secure-key"})

        # Should be 200 OK (success)
        assert response.status_code == 200
        assert response.json()["success"] is True

    app.dependency_overrides.clear()
