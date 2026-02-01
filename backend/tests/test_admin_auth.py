import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.config import get_settings, Settings

client = TestClient(app)

def mock_settings_with_key():
    s = Settings()
    s.admin_secret_key = "secret123"
    return s

def mock_settings_without_key():
    s = Settings()
    s.admin_secret_key = ""
    return s

def test_endpoint_protected_no_key_configured():
    app.dependency_overrides[get_settings] = mock_settings_without_key

    # reset-stuck is POST
    response = client.post("/api/files/reset-stuck", headers={"X-Admin-Key": "anything"})

    assert response.status_code == 500
    assert "Admin access not configured" in response.json()["detail"]

    app.dependency_overrides = {}

def test_endpoint_protected_invalid_key():
    app.dependency_overrides[get_settings] = mock_settings_with_key

    response = client.post("/api/files/reset-stuck", headers={"X-Admin-Key": "wrong"})
    assert response.status_code == 401
    assert "Invalid or missing admin key" in response.json()["detail"]

    response = client.post("/api/files/reset-stuck") # No header
    assert response.status_code == 401
    assert "Invalid or missing admin key" in response.json()["detail"]

    app.dependency_overrides = {}

from unittest.mock import patch

def test_endpoint_protected_valid_key():
    app.dependency_overrides[get_settings] = mock_settings_with_key

    # We need to patch the supabase reference inside the router module
    with patch("app.routers.files_router.supabase") as mock_supa:
        # Setup mock return for the query: supabase.table().select().eq().lt().execute()
        mock_supa.table.return_value.select.return_value.eq.return_value.lt.return_value.execute.return_value.data = []

        response = client.post("/api/files/reset-stuck", headers={"X-Admin-Key": "secret123"})

        assert response.status_code == 200
        assert response.json()["success"] is True

    app.dependency_overrides = {}
