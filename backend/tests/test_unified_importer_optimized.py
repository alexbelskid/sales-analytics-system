import pytest
from unittest.mock import MagicMock, patch
import pandas as pd
from app.services.unified_importer import UnifiedImporter

# Mock supabase at module level
@pytest.fixture
def mock_supabase():
    with patch('app.services.unified_importer.supabase') as mock:
        yield mock

def create_mock_response(data):
    response = MagicMock()
    response.data = data
    return response

def insert_side_effect(data):
    if isinstance(data, list):
        return MagicMock(select=MagicMock(return_value=MagicMock(execute=MagicMock(return_value=create_mock_response(
            [dict(item, id=f"mock-id-{i}") for i, item in enumerate(data)]
        )))))
    return MagicMock(select=MagicMock(return_value=MagicMock(execute=MagicMock(return_value=create_mock_response(
        [dict(data, id="mock-id-single")]
    )))))

@pytest.mark.asyncio
async def test_import_sales_batching_optimization(mock_supabase):
    # Setup mock behavior
    # Handle table().select().in_().execute() -> returns empty list initially
    mock_supabase.table.return_value.select.return_value.in_.return_value.execute.return_value = create_mock_response([])

    # Handle table().insert() -> returns mocked data with IDs
    mock_supabase.table.return_value.insert.side_effect = insert_side_effect

    # Handle table().select().eq().execute() (legacy/fallback)
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = create_mock_response([])

    # Create test data (1000 rows)
    df = pd.DataFrame({
        'customer_name': [f'Customer {i % 100}' for i in range(1000)],
        'date': ['2023-01-01'] * 1000,
        'amount': [100.0] * 1000,
        'product_name': [f'Product {i % 100}' for i in range(1000)],
        'quantity': [1] * 1000,
        'price': [100.0] * 1000
    })

    importer = UnifiedImporter()
    result = await importer._import_sales(df, mode="append", import_id="test-opt")

    assert result['success'] is True, f"Import failed: {result.get('errors')}"
    assert result['imported_rows'] == 1000

    # Verify low number of calls (should be small, e.g. < 20 for 2 batches)
    call_count = mock_supabase.table.call_count
    print(f"Total DB calls: {call_count}")
    assert call_count < 50, f"Too many DB calls: {call_count}. N+1 optimization might be broken."
