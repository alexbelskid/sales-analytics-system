import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import os
import sys

# Set environment to prevent loading real credentials
os.environ["ADMIN_SECRET_KEY"] = "unsafe-default-secret-key"

from app.main import app
from app.config import settings

client = TestClient(app)

def test_delete_all_data_no_auth():
    """Verify delete-all-data requires admin key"""
    response = client.delete("/api/files/delete-all-data")
    assert response.status_code == 403
    assert response.json() == {"detail": "Admin key required"}

def test_delete_all_data_invalid_auth():
    """Verify delete-all-data rejects invalid admin key"""
    response = client.delete(
        "/api/files/delete-all-data",
        headers={"X-Admin-Key": "wrong-key"}
    )
    assert response.status_code == 403
    assert response.json() == {"detail": "Invalid admin key"}

def test_delete_all_data_valid_auth():
    """Verify delete-all-data accepts valid admin key"""
    # Fix patching: patch app.services.forecast_service.ForecastService
    with patch("app.database.get_supabase_admin") as mock_get_admin, \
         patch("app.routers.files_router.supabase") as mock_supabase, \
         patch("app.services.cache_service.cache") as mock_cache, \
         patch("app.services.forecast_service.ForecastService") as mock_forecast:

        # Setup mock db
        mock_db = MagicMock()
        mock_get_admin.return_value = mock_db

        # Mock table().select().execute() chain for import history
        mock_db.table.return_value.select.return_value.execute.return_value.data = []

        # Mock RPC success
        mock_db.rpc.return_value.execute.return_value = None

        # Ensure config has the expected key
        expected_key = settings.admin_secret_key

        # Perform request with correct key
        response = client.delete(
            "/api/files/delete-all-data",
            headers={"X-Admin-Key": expected_key}
        )

        # Should be 200 OK
        assert response.status_code == 200
        assert response.json()["success"] is True

def test_delete_all_sales_no_auth():
    """Verify delete-all-sales requires admin key"""
    response = client.delete("/api/files/all-sales")
    assert response.status_code == 403

def test_delete_all_sales_valid_auth():
    """Verify delete-all-sales accepts valid admin key"""
    with patch("app.routers.files_router.supabase") as mock_supabase, \
         patch("app.services.cache_service.cache") as mock_cache:

        # Mock count check
        mock_supabase.table.return_value.select.return_value.execute.return_value.count = 0

        expected_key = settings.admin_secret_key

        response = client.delete(
            "/api/files/all-sales",
            headers={"X-Admin-Key": expected_key}
        )

        assert response.status_code == 200

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
