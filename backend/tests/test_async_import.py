import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient
import pandas as pd
import sys
import os

# Ensure app can be imported
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

# We need to mock supabase before importing app.main because of top-level usage
with patch("app.database.supabase", MagicMock()):
    from app.main import app

client = TestClient(app)

@pytest.fixture
def mock_read_csv():
    with patch("app.routers.unified_import.pd.read_csv") as mock:
        df = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
        mock.return_value = df
        yield mock

@pytest.fixture
def mock_read_excel():
    with patch("app.routers.unified_import.pd.read_excel") as mock:
        df = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
        mock.return_value = df
        yield mock

@pytest.fixture
def mock_importer():
    with patch("app.routers.unified_import.UnifiedImporter") as mock:
        instance = mock.return_value
        instance.import_data = AsyncMock(return_value=MagicMock(
            success=True,
            import_id="test-id",
            data_type="test",
            imported_rows=2,
            failed_rows=0,
            errors=[],
            message="Success"
        ))
        # Static method mock needs to be on the class or patched where imported
        mock.detect_data_type.return_value = "sales"
        yield instance

def test_unified_upload_csv_calls_pandas(mock_read_csv, mock_importer):
    """Test that CSV upload calls pandas read_csv"""
    csv_content = b"col1,col2\n1,3\n2,4"
    files = {"file": ("test.csv", csv_content, "text/csv")}

    # We mock os.unlink to avoid error when deleting temp file that pandas didn't actually read
    with patch("os.unlink"):
        response = client.post("/api/import/unified", files=files, data={"mode": "append"})

    assert response.status_code == 200
    assert response.json()["success"] is True

    # Verify pd.read_csv was called
    assert mock_read_csv.called

def test_detect_type_excel_calls_pandas(mock_read_excel):
    """Test that detect type calls pandas read_excel"""
    excel_content = b"fake-excel-content"
    files = {"file": ("test.xlsx", excel_content, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}

    with patch("app.routers.unified_import.UnifiedImporter.detect_data_type", return_value="sales"):
        with patch("os.unlink"):
             response = client.post("/api/import/detect-type", files=files)

    assert response.status_code == 200
    assert response.json()["detected_type"] == "sales"

    # Verify pd.read_excel was called
    assert mock_read_excel.called
