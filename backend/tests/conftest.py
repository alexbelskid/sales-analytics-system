import pytest
from unittest.mock import MagicMock, patch
import sys

@pytest.fixture(scope="session", autouse=True)
def mock_supabase():
    """
    Mock Supabase client for all tests to prevent connection errors
    and avoid needing real credentials.
    """
    mock = MagicMock()

    # Default return values to prevent crashes
    mock.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []
    mock.table.return_value.insert.return_value.execute.return_value.data = [{"id": "mock-id"}]
    mock.table.return_value.update.return_value.eq.return_value.execute.return_value.data = []
    mock.table.return_value.delete.return_value.neq.return_value.execute.return_value.data = []

    # Handle the chained calls often used
    # e.g. supabase.table().select().in_().execute()
    mock.table.return_value.select.return_value.in_.return_value.execute.return_value.data = []

    # Patch relevant locations
    # app.database is the source of truth
    # app.services.unified_importer imports it as 'supabase'

    p1 = patch("app.database.supabase", mock)
    p2 = patch("app.database.supabase_admin", mock)
    # We also need to patch where it's imported in unified_importer because "from x import y" binds y early
    p3 = patch("app.services.unified_importer.supabase", mock)

    with p1, p2, p3:
        yield mock
