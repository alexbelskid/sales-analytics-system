from fastapi.testclient import TestClient
from app.main import app
from app.config import settings
from unittest.mock import patch, MagicMock

client = TestClient(app)

# Use a test secret key
TEST_ADMIN_KEY = "test-secret-key-123"

def test_delete_all_data_no_key():
    """Verify 403 Forbidden when no admin key provided"""
    # Ensure key is configured
    settings.admin_secret_key = TEST_ADMIN_KEY

    response = client.delete("/api/files/delete-all-data")
    assert response.status_code == 403
    assert response.json()["detail"] == "Invalid or missing Admin Key"

def test_delete_all_data_wrong_key():
    """Verify 403 Forbidden when wrong admin key provided"""
    settings.admin_secret_key = TEST_ADMIN_KEY

    response = client.delete(
        "/api/files/delete-all-data",
        headers={"X-Admin-Key": "wrong-key"}
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Invalid or missing Admin Key"

def test_delete_all_data_success_mocked():
    """Verify 200 OK (or at least auth pass) when correct key provided"""
    settings.admin_secret_key = TEST_ADMIN_KEY

    # Patch app.database.get_supabase_admin instead of local import
    with patch("app.database.get_supabase_admin") as mock_get_admin:
        mock_client = MagicMock()
        mock_get_admin.return_value = mock_client

        # Mock table().select().execute() for imports retrieval
        mock_client.table.return_value.select.return_value.execute.return_value.data = []

        # Mock rpc().execute()
        mock_client.rpc.return_value.execute.return_value = None

        # Mock storage
        mock_client.storage.from_.return_value.remove.return_value = None

        # Mock other potential calls (fallback deletes)
        mock_client.table.return_value.delete.return_value.neq.return_value.execute.return_value.data = []
        mock_client.table.return_value.delete.return_value.gte.return_value.execute.return_value.data = []
        mock_client.table.return_value.delete.return_value.in_.return_value.execute.return_value.data = []

        # Also mock cache service to avoid redis/memory errors if any
        with patch("app.services.cache_service.cache.clear") as mock_clear:
            mock_clear.return_value = 0
            # Also mock invalidate_pattern
            with patch("app.services.cache_service.cache.invalidate_pattern"):

                response = client.delete(
                    "/api/files/delete-all-data",
                    headers={"X-Admin-Key": TEST_ADMIN_KEY}
                )

                # It should not be 403
                assert response.status_code != 403

                # Should be 200
                assert response.status_code == 200, f"Response: {response.text}"
                assert response.json()["success"] is True

def test_reset_stuck_imports_auth():
    """Verify reset-stuck endpoint is protected"""
    settings.admin_secret_key = TEST_ADMIN_KEY

    # No key
    response = client.post("/api/files/reset-stuck")
    assert response.status_code == 403

    # Correct key (mocking DB to avoid errors)
    with patch("app.routers.files_router.supabase") as mock_db:
        # Mock select query: table -> select -> eq -> lt -> execute
        mock_db.table.return_value.select.return_value.eq.return_value.lt.return_value.execute.return_value.data = []

        response = client.post(
            "/api/files/reset-stuck",
            headers={"X-Admin-Key": TEST_ADMIN_KEY}
        )
        assert response.status_code == 200
        assert response.json()["success"] is True

def test_delete_file_auth():
    """Verify delete file endpoint is protected"""
    settings.admin_secret_key = TEST_ADMIN_KEY

    # No key
    response = client.delete("/api/files/some-uuid")
    assert response.status_code == 403

    # Correct key
    with patch("app.routers.files_router.supabase") as mock_db:
        # Mock select query to find file
        mock_db.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [{"id": "some-uuid", "filename": "test.csv"}]

        # Mock delete return object
        mock_execute_res = MagicMock()
        mock_execute_res.data = [] # empty list implies 0 deleted, which is fine

        # Mock delete chain
        mock_db.table.return_value.delete.return_value.eq.return_value.execute.return_value = mock_execute_res

        # Mock storage remove
        mock_db.storage.from_.return_value.remove.return_value = None

        # Mock cache service
        with patch("app.services.cache_service.cache"):
            response = client.delete(
                "/api/files/some-uuid",
                headers={"X-Admin-Key": TEST_ADMIN_KEY}
            )
            assert response.status_code == 200
