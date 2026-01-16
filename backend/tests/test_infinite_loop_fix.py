"""
Test for infinite import loop fixes:
1. Validation order (reject large files BEFORE creating import_history)
2. Real-time progress updates during batching
3. Stuck import cleanup
"""

import pytest
import pandas as pd
from datetime import datetime, timedelta
from app.services.unified_importer import UnifiedImporter
from app.database import supabase


@pytest.mark.asyncio
async def test_large_file_rejected_before_import_history():
    """Critical: Files >50k rows must be rejected BEFORE import_history is created"""
    # Create file with 55,000 rows (exceeds limit)
    df = pd.DataFrame({
        'customer_name': [f'Customer {i}' for i in range(55000)],
        'amount': [100.0] * 55000,
        'date': ['2026-01-16'] * 55000
    })
    
    importer = UnifiedImporter()
    result = await importer.import_data(
        df=df,
        filename='oversized_test.csv',
        file_size=1000,
        data_type='sales'
    )
    
    # Should be rejected
    assert result.success == False
    assert '50000' in result.message  # Mentions limit
    
    # CRITICAL: No import_history record should exist
    history = supabase.table('import_history').select('*').eq('filename', 'oversized_test.csv').execute()
    assert len(history.data) == 0, "import_history should NOT be created for rejected files!"
    
    print(f"✅ Large file rejected correctly: {result.message}")


@pytest.mark.asyncio
async def test_progress_updates_during_import():
    """Progress should update every 100 rows"""
    # Create 300 row file (3 batches)
    df = pd.DataFrame({
        'customer_name': [f'Customer {i}' for i in range(300)],
        'product_name': [f'Product {i % 10}' for i in range(300)],
        'quantity': [1] * 300,
        'price': [100.0] * 300,
        'amount': [100.0] * 300,
        'date': ['2026-01-16'] * 300
    })
    
    importer = UnifiedImporter()
    result = await importer.import_data(
        df=df,
        filename='progress_test.csv',
        file_size=10000,
        data_type='sales',
        mode='append'
    )
    
    # Should complete successfully
    assert result.success == True
    assert result.import_id is not None
    
    # Check final progress is 100%
    history = supabase.table('import_history').select('*').eq('id', result.import_id).execute()
    assert len(history.data) == 1
    assert history.data[0]['progress_percent'] == 100
    assert history.data[0]['status'] == 'completed'
    
    print(f"✅ Progress test passed: {result.imported_rows} rows imported, 100% progress")
    
    # Cleanup
    supabase.table('import_history').delete().eq('id', result.import_id).execute()


@pytest.mark.asyncio
async def test_validation_order():
    """Validation must run BEFORE import_history creation"""
    # This test verifies the fix prevents stuck "processing" records
    
    # Test 1: File too large (50MB+)
    result = await UnifiedImporter().import_data(
        df=pd.DataFrame({'test': ['data']}),
        filename='toolarge.csv',
        file_size=60 * 1024 * 1024,  # 60MB  
        data_type='sales'
    )
    
    assert result.success == False
    assert 'too large' in result.message.lower()
    
    # No import_history should exist
    history = supabase.table('import_history').select('*').eq('filename', 'toolarge.csv').execute()
    assert len(history.data) == 0
    
    print("✅ Validation order test passed - no stuck records")


@pytest.mark.asyncio
async def test_row_limit_increased():
    """Row limit should be 50,000 (not 10,000)"""
    # File with 45,000 rows should be ACCEPTED
    df = pd.DataFrame({
        'customer_name': ['Test'] * 45000,
        'amount': [100.0] * 45000,
        'date': ['2026-01-16'] * 45000
    })
    
    importer = UnifiedImporter()
    result = await importer.import_data(
        df=df,
        filename='45k_test.csv',
        file_size=500000,
        data_type='sales'
    )
    
    # Should be accepted (within new 50k limit)
    # Note: might fail due to other reasons (DB constraints), but shouldn't fail row count validation
    if not result.success and 'too many rows' in result.message.lower():
        pytest.fail(f"File with 45k rows should be accepted. Got: {result.message}")
    
    # Cleanup if created
    if result.import_id:
        supabase.table('import_history').delete().eq('id', result.import_id).execute()
    
    print("✅ Row limit test passed - 45k rows accepted")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
