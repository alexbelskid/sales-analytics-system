
import pytest
import pandas as pd
from unittest.mock import MagicMock, patch
from app.services.unified_importer import UnifiedImporter

@pytest.fixture
def mock_supabase():
    with patch('app.services.unified_importer.supabase') as mock:
        # Setup basic mock structure
        mock.table.return_value = mock
        mock.select.return_value = mock
        mock.eq.return_value = mock
        mock.in_.return_value = mock
        mock.insert.return_value = mock
        mock.delete.return_value = mock
        mock.neq.return_value = mock

        # Default execute return
        mock.execute.return_value = MagicMock(data=[])
        yield mock

@pytest.mark.asyncio
async def test_import_customers_batching(mock_supabase):
    """Test customer import with batching optimization"""
    # Create DataFrame
    num_rows = 50
    df = pd.DataFrame({
        'name': [f'Customer {i}' for i in range(num_rows)],
        'email': [f'customer{i}@example.com' for i in range(num_rows)],
        'phone': [f'555-{i:04d}' for i in range(num_rows)],
        'company': [f'Company {i}' for i in range(num_rows)]
    })

    importer = UnifiedImporter()
    result = await importer._import_customers(df, mode="append", import_id="test-id")

    assert result['success'] is True
    assert result['imported_rows'] == num_rows
    assert result['failed_rows'] == 0

    # Verify optimization:
    # 1. Pre-fetch check (in_)
    # 2. Bulk insert (insert called with list)

    # Check in_ was called
    assert mock_supabase.in_.called

    # Check insert was called with a list (bulk insert)
    # We might have multiple insert calls if we had fallbacks or multiple batches,
    # but for 50 rows, it should be one batch.
    insert_calls = mock_supabase.insert.call_args_list
    assert len(insert_calls) > 0

    # Find the bulk insert call
    bulk_insert_found = False
    for call in insert_calls:
        args, _ = call
        if args and isinstance(args[0], list):
            bulk_insert_found = True
            assert len(args[0]) == num_rows
            break

    assert bulk_insert_found

@pytest.mark.asyncio
async def test_import_customers_duplicates(mock_supabase):
    """Test handling of duplicates"""
    # Create DataFrame
    df = pd.DataFrame({
        'name': ['Customer 1', 'Customer 2', 'Customer 1'], # 'Customer 1' is duplicate in file
    })

    # Mock pre-existing customer in DB
    def mock_execute(*args, **kwargs):
        # If in_ is called, return 'Customer 2' as existing
        # This is tricky because execute is called for both select and insert
        # We need to distinguish based on the chain.
        # But here we just mock the return value of execute on the mock object.
        # This is hard because the chain returns the same mock object.
        return MagicMock(data=[])

    # Better approach: check side effects or configure based on call
    # But since we use the same mock object for everything, it's stateful.

    # Let's just mock that 'Customer 2' exists when `in_` returns
    mock_supabase.execute.side_effect = [
        MagicMock(data=[{'name': 'Customer 2'}]), # 1st call: in_ (pre-fetch)
        MagicMock(data=[]) # 2nd call: insert (bulk)
    ]

    importer = UnifiedImporter()
    result = await importer._import_customers(df, mode="append", import_id="test-id")

    # Customer 1 (row 0): New -> Inserted
    # Customer 2 (row 1): Exists in DB -> Failed
    # Customer 1 (row 2): Duplicate in file -> Failed

    assert result['imported_rows'] == 1
    assert result['failed_rows'] == 2

    # Verify what was inserted
    insert_calls = mock_supabase.insert.call_args_list
    # Expected: one bulk insert with 1 record (Customer 1)
    args, _ = insert_calls[0]
    assert len(args[0]) == 1
    assert args[0][0]['name'] == 'Customer 1'

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
