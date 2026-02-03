
import pytest
import os
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app
from app.config import get_settings

client = TestClient(app)

# Mock settings to inject admin key
def mock_settings_with_key():
    settings = get_settings()
    settings.admin_secret_key = "secure-secret-key"
    return settings

def test_admin_auth_flow():
    """
    Test the full admin authentication flow:
    1. Missing key in server config -> 500
    2. Missing header in request -> 401
    3. Invalid header -> 403
    4. Valid header -> 200 (Success)
    """

    # Mock get_supabase_admin to avoid actual DB calls
    with patch("app.database.get_supabase_admin") as mock_db:
        mock_client = MagicMock()
        mock_db.return_value = mock_client
        mock_client.table.return_value.select.return_value.execute.return_value.data = []
        mock_client.rpc.return_value.execute.return_value = None

        # Case 1: Server not configured (Default behavior in test env)
        # We need to make sure dependency override is NOT active or clears it
        app.dependency_overrides = {}
        # Note: Depending on how settings are loaded, this might still have empty key
        # verify_admin_access checks settings.admin_secret_key

        # To test Case 1 properly, we rely on the default config which has empty key
        response = client.delete("/api/files/delete-all-data")
        assert response.status_code == 500
        assert response.json()["detail"] == "Admin access not configured on server"

        # Now override settings for remaining cases
        app.dependency_overrides[get_settings] = mock_settings_with_key

        # But wait, verify_admin_access imports settings directly from app.config
        # So dependency_overrides won't work if verify_admin_access uses `from app.config import settings`
        # Let's check dependencies.py
        # It does: `from app.config import settings`

        # So we must patch `app.dependencies.settings`
        with patch("app.dependencies.settings") as mock_settings:
            mock_settings.admin_secret_key = "secure-secret-key"

            # Case 2: Missing Header
            response = client.delete("/api/files/delete-all-data")
            assert response.status_code == 401
            assert response.json()["detail"] == "Admin key required"

            # Case 3: Invalid Header
            response = client.delete("/api/files/delete-all-data", headers={"X-Admin-Key": "wrong-key"})
            assert response.status_code == 403
            assert response.json()["detail"] == "Invalid admin key"

            # Case 4: Valid Header
            response = client.delete("/api/files/delete-all-data", headers={"X-Admin-Key": "secure-secret-key"})
            assert response.status_code == 200
            assert response.json()["success"] == True

if __name__ == "__main__":
    test_admin_auth_flow()
