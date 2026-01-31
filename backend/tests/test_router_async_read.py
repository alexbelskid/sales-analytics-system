import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from fastapi import UploadFile, BackgroundTasks
from app.routers.unified_import import unified_upload, detect_data_type
import pandas as pd
import asyncio

@pytest.mark.asyncio
async def test_unified_upload_uses_async_read(mock_supabase):
    """
    Verify that unified_upload uses asyncio.to_thread for reading CSV/Excel
    to avoid blocking the event loop.
    """
    # Mock UploadFile
    mock_file = MagicMock(spec=UploadFile)
    mock_file.filename = "test.csv"
    mock_file.read = AsyncMock(return_value=b"col1,col2\n1,2")

    # Mock pandas DataFrame
    mock_df = pd.DataFrame({'col1': [1], 'col2': [2]})

    # Mock dependencies
    # We mock asyncio.to_thread to verify it's used
    # We mock pd.read_csv/excel to avoid actual file I/O

    with patch("app.routers.unified_import.UnifiedImporter") as MockImporter, \
         patch("app.routers.unified_import.pd.read_csv") as mock_read_csv, \
         patch("app.routers.unified_import.asyncio.to_thread", new_callable=AsyncMock) as mock_to_thread:

        # Setup mocks
        mock_to_thread.return_value = mock_df
        mock_read_csv.return_value = mock_df # In case it's called synchronously (old code)

        MockImporter.return_value.import_data = AsyncMock(return_value=MagicMock(
            success=True,
            import_id="123",
            data_type="sales",
            imported_rows=1,
            failed_rows=0,
            message="ok",
            errors=[]
        ))

        # Call the endpoint function directly
        await unified_upload(
            background_tasks=MagicMock(spec=BackgroundTasks),
            file=mock_file,
            data_type="sales",
            mode="append",
            period_start=None,
            period_end=None
        )

        # Verify asyncio.to_thread was called
        # This assert should FAIL on the current code
        assert mock_to_thread.called, "asyncio.to_thread should be called for non-blocking I/O"

        # Verify it was called with read_csv
        args, _ = mock_to_thread.call_args
        # The first arg to to_thread should be the function
        assert args[0] == pd.read_csv or args[0] == mock_read_csv

@pytest.mark.asyncio
async def test_detect_type_uses_async_read(mock_supabase):
    """
    Verify that detect_data_type uses asyncio.to_thread
    """
    mock_file = MagicMock(spec=UploadFile)
    mock_file.filename = "test.xlsx"
    mock_file.read = AsyncMock(return_value=b"fake content")

    mock_df = pd.DataFrame({'col1': [1]})

    with patch("app.routers.unified_import.UnifiedImporter") as MockImporter, \
         patch("app.routers.unified_import.pd.read_excel") as mock_read_excel, \
         patch("app.routers.unified_import.asyncio.to_thread", new_callable=AsyncMock) as mock_to_thread:

        mock_to_thread.return_value = mock_df
        mock_read_excel.return_value = mock_df

        MockImporter.detect_data_type.return_value = "sales"

        await detect_data_type(file=mock_file)

        assert mock_to_thread.called, "asyncio.to_thread should be called"
        args, _ = mock_to_thread.call_args
        assert args[0] == pd.read_excel or args[0] == mock_read_excel
