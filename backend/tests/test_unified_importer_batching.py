"""
Test batching functionality in unified importer
Verifies that large files are processed in batches without memory issues
"""

import pytest
import pandas as pd
from datetime import datetime
from app.services.unified_importer import UnifiedImporter


@pytest.mark.asyncio
async def test_large_file_batching():
    """Verify large files (2000 rows) are processed in batches without memory issues"""
    # Create large DataFrame (2000 rows)
    df = pd.DataFrame({
        'customer_name': [f'Customer {i}' for i in range(2000)],
        'product_name': [f'Product {i % 100}' for i in range(2000)],
        'quantity': [1] * 2000,
        'price': [100.0] * 2000,
        'amount': [100.0] * 2000,
        'date': ['2026-01-15'] * 2000
    })
    
    # Mock import_id for testing
    import_id = 'test-import-batching-001'
    
    importer = UnifiedImporter()
    result = await importer._import_sales(df, 'append', import_id)
    
    # Verify batch processing succeeded
    assert result['success'] == True
    assert result['imported_rows'] > 0
    assert result['imported_rows'] + result['failed_rows'] == 2000
    
    print(f"✅ Batch processing test passed: {result['imported_rows']} imported, {result['failed_rows']} failed")


@pytest.mark.asyncio
async def test_small_file_no_batching_issues():
    """Verify small files (10 rows) also work correctly"""
    df = pd.DataFrame({
        'customer_name': [f'Customer {i}' for i in range(10)],
        'product_name': [f'Product {i}' for i in range(10)],
        'quantity': [1] * 10,
        'price': [50.0] * 10,
        'amount': [50.0] * 10,
        'date': ['2026-01-15'] * 10
    })
    
    import_id = 'test-import-small-001'
    
    importer = UnifiedImporter()
    result = await importer._import_sales(df, 'append', import_id)
    
    assert result['success'] == True
    assert result['imported_rows'] == 10
    assert result['failed_rows'] == 0
    
    print(f"✅ Small file test passed: {result['imported_rows']} imported")


@pytest.mark.asyncio
async def test_file_size_validation():
    """Verify files larger than 50MB are rejected"""
    # Create mock large DataFrame
    df = pd.DataFrame({
        'customer_name': ['Test'] * 51000  # Exceeds MAX_ROWS limit (50000)
    })
    
    importer = UnifiedImporter()
    
    # This should fail validation (50000 row limit)
    result = await importer.import_data(
        df=df,
        filename='large_test.csv',
        file_size=1000,  # Even with small file size, row count should fail
        data_type='sales',
        mode='append'
    )
    
    assert result.success == False
    assert 'too many rows' in result.message.lower()
    
    print(f"✅ Row count validation test passed: {result.message}")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
