import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app

# Create test client
client = TestClient(app)

def test_admin_auth_flow():
    # We need to patch the settings object that is imported in dependencies.py
    # Since dependencies.py does `from app.config import settings`, we should patch `app.dependencies.settings`

    with patch("app.dependencies.settings") as mock_settings:
        mock_settings.admin_secret_key = "secure-test-key-123"

        # Test 1: Missing Header
        response = client.post("/api/files/reset-stuck")
        assert response.status_code == 401
        assert "Missing X-Admin-Key header" in response.json()["detail"]

        # Test 2: Invalid Header
        response = client.post(
            "/api/files/reset-stuck",
            headers={"X-Admin-Key": "wrong-key"}
        )
        assert response.status_code == 401
        assert "Invalid admin key" in response.json()["detail"]

        # Test 3: Valid Header
        # Note: The endpoint will likely fail 500 inside due to DB connection issues in test env,
        # but getting anything other than 401 means Auth passed.
        response = client.post(
            "/api/files/reset-stuck",
            headers={"X-Admin-Key": "secure-test-key-123"}
        )
        assert response.status_code != 401
        print(f"Passed auth with status: {response.status_code}")

def test_admin_auth_not_configured():
    """Test fail secure when key is not set"""
    with patch("app.dependencies.settings") as mock_settings:
        mock_settings.admin_secret_key = "" # Empty

        response = client.post(
            "/api/files/reset-stuck",
            headers={"X-Admin-Key": "any-key"}
        )
        assert response.status_code == 500
        assert "not configured" in response.json()["detail"]

if __name__ == '__main__':
    # Add backend to pythonpath
    import sys
    import os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    pytest.main([__file__, '-v'])
