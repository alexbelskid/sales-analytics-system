
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_delete_all_data_no_server_config():
    """
    Test that if the server has no admin key configured, it returns 500 (Fail Secure).
    """
    # Ensure settings.admin_secret_key is empty
    with patch("app.dependencies.settings.admin_secret_key", ""):
        # We don't need to mock database here because it should fail before hitting DB logic
        response = client.delete("/api/files/delete-all-data")

        assert response.status_code == 500
        assert "not configured" in response.json()["detail"]


def test_delete_all_data_unauthorized():
    """
    Test that if admin key IS configured, but request has no header, it returns 401.
    """
    # Mock settings to have a key
    with patch("app.dependencies.settings.admin_secret_key", "secret123"):
        response = client.delete("/api/files/delete-all-data")

        assert response.status_code == 401
        assert "Missing admin key" in response.json()["detail"]


def test_delete_all_data_wrong_key():
    """
    Test that if request has WRONG key, it returns 401.
    """
    with patch("app.dependencies.settings.admin_secret_key", "secret123"):
        response = client.delete(
            "/api/files/delete-all-data",
            headers={"X-Admin-Key": "wrong_key"}
        )

        assert response.status_code == 401
        assert "Invalid admin key" in response.json()["detail"]


def test_delete_all_data_authorized():
    """
    Test that if request has CORRECT key, it proceeds (and returns 200).
    """
    with patch("app.dependencies.settings.admin_secret_key", "secret123"):
        # Now we need to mock DB because it will proceed to controller logic
        with patch("app.database.get_supabase_admin") as mock_get_admin:
            mock_db = MagicMock()
            mock_get_admin.return_value = mock_db

            # Mock DB responses to avoid errors in logic
            mock_db.table.return_value.select.return_value.execute.return_value.data = []
            mock_db.rpc.return_value.execute.side_effect = Exception("RPC failed, fallback to batch")
            mock_db.table.return_value.delete.return_value.neq.return_value.execute.return_value = None

            response = client.delete(
                "/api/files/delete-all-data",
                headers={"X-Admin-Key": "secret123"}
            )

            assert response.status_code == 200
            assert response.json()["success"] is True
