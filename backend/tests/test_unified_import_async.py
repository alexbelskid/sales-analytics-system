import pytest
import sys
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import UploadFile, BackgroundTasks
from app.routers.unified_import import detect_data_type, unified_upload

# Create the test file
@pytest.mark.asyncio
async def test_detect_data_type_async_csv():
    # Mock pandas
    with patch('app.routers.unified_import.pd') as mock_pd:
        # Setup mock df
        mock_df = MagicMock()
        mock_df.columns.tolist.return_value = ['col1', 'col2']
        mock_df.head.return_value.to_dict.return_value = []
        mock_df.__len__.return_value = 10

        # When read_csv is called, return mock_df
        mock_pd.read_csv.return_value = mock_df

        # Mock UnifiedImporter.detect_data_type
        # We need to patch where it is imported in the router
        with patch('app.routers.unified_import.UnifiedImporter') as mock_importer_cls:
            mock_importer_cls.detect_data_type.return_value = 'sales'

            # Create a mock file
            file = MagicMock(spec=UploadFile)
            file.filename = 'test.csv'
            file.read = AsyncMock(return_value=b'content')

            # Call the function
            result = await detect_data_type(file)

            # Verify read_csv was called
            # Since we are running in an event loop, asyncio.to_thread should execute the sync function in a thread.
            mock_pd.read_csv.assert_called_once()

            # Verify result
            assert result['detected_type'] == 'sales'

@pytest.mark.asyncio
async def test_unified_upload_async_excel():
    # Mock pandas
    with patch('app.routers.unified_import.pd') as mock_pd:
        # Setup mock df
        mock_df = MagicMock()
        mock_df.columns.tolist.return_value = ['col1']
        mock_df.__len__.return_value = 10

        # When read_excel is called, return mock_df
        mock_pd.read_excel.return_value = mock_df

        # Mock UnifiedImporter instance
        mock_importer_instance = AsyncMock()
        mock_importer_instance.import_data.return_value = MagicMock(
            success=True, import_id='123', data_type='sales',
            imported_rows=10, failed_rows=0, message='ok', errors=[]
        )

        with patch('app.routers.unified_import.UnifiedImporter', return_value=mock_importer_instance):
            # Create a mock file
            file = MagicMock(spec=UploadFile)
            file.filename = 'test.xlsx'
            file.read = AsyncMock(return_value=b'content')

            # Call the function
            result = await unified_upload(
                background_tasks=MagicMock(spec=BackgroundTasks),
                file=file,
                data_type='sales',
                mode='append',
                period_start=None,
                period_end=None
            )

            # Verify read_excel was called
            mock_pd.read_excel.assert_called_once()

            # Verify import_data was called
            mock_importer_instance.import_data.assert_called_once()
            assert result['success'] is True
