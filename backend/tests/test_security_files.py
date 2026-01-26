import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app
from app.config import settings

client = TestClient(app)

def test_delete_all_data_unauthorized():
    """
    Test that the delete-all-data endpoint is protected.
    """
    response = client.delete("/api/files/delete-all-data")
    assert response.status_code in [401, 403, 422], f"Expected security failure, got {response.status_code}"

def test_delete_all_data_authorized():
    """
    Test that the endpoint is accessible with the correct key.
    """
    # Mock settings.admin_secret_key in dependencies
    with patch("app.dependencies.settings.admin_secret_key", "test_secret"), \
         patch("app.database.get_supabase_admin") as mock_get_db, \
         patch("app.config.settings.storage_bucket", "test-bucket"), \
         patch("app.services.cache_service.cache") as mock_cache:

            # Setup DB mock
            mock_db = MagicMock()
            mock_get_db.return_value = mock_db

            # Mock DB chains
            mock_db.table.return_value.select.return_value.execute.return_value.data = []
            mock_db.rpc.return_value.execute.return_value = MagicMock()
            mock_db.table.return_value.delete.return_value.neq.return_value.execute.return_value = MagicMock()
            mock_db.table.return_value.delete.return_value.gte.return_value.execute.return_value = MagicMock()

            headers = {"X-Admin-Key": "test_secret"}
            response = client.delete("/api/files/delete-all-data", headers=headers)

            # Debug output if assertion fails
            if response.status_code != 200:
                print(f"Failed with {response.status_code}: {response.text}")

            assert response.status_code == 200
            assert response.json()["success"] is True

def test_delete_file_unauthorized():
    """Test protection on single file delete"""
    response = client.delete("/api/files/some-uuid")
    assert response.status_code in [401, 403, 422]

def test_delete_sales_data_unauthorized():
    """Test protection on sales data delete"""
    response = client.delete("/api/files/sales-data/some-uuid")
    assert response.status_code in [401, 403, 422]

def test_delete_all_sales_unauthorized():
    """Test protection on all sales delete"""
    response = client.delete("/api/files/all-sales")
    assert response.status_code in [401, 403, 422]
