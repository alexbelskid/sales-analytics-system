#!/usr/bin/env python3
"""
Test script to verify import works with large files (50K+ rows)
Run this to test the import system before uploading via UI
"""

import asyncio
import pandas as pd
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.unified_importer import UnifiedImporter
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_large_import():
    """Test importing a large synthetic dataset"""
    
    print("=" * 80)
    print("TESTING LARGE FILE IMPORT (10,000 rows)")
    print("=" * 80)
    
    # Create test DataFrame with 10000 rows
    print("\n📝 Creating synthetic data...")
    num_rows = 10000
    
    data = {
        'customer_name': [f'Customer {i%1000}' for i in range(num_rows)],
        'product_name': [f'Product {i%500}' for i in range(num_rows)],
        'quantity': [i % 10 + 1 for i in range(num_rows)],
        'price': [100 + (i % 1000) for i in range(num_rows)],
        'amount': [(i % 10 + 1) * (100 + (i % 1000)) for i in range(num_rows)],
        'date': ['2025-12-01' for _ in range(num_rows)]
    }
    
    df = pd.DataFrame(data)
    print(f"✅ Created DataFrame with {len(df)} rows")
    print(f"   Columns: {list(df.columns)}")
    
    # Test import
    print("\n🚀 Starting import test...")
    importer = UnifiedImporter()
    
    result = await importer.import_data(
        df=df,
        filename="test_large_file.xlsx",
        file_size=len(df) * 100,  # Approximate size
        data_type="sales",
        mode="append"
    )
    
    # Show results
    print("\n" + "=" * 80)
    print("RESULTS:")
    print("=" * 80)
    print(f"Success: {result.success}")
    print(f"Imported: {result.imported_rows}")
    print(f"Failed: {result.failed_rows}")
    print(f"Import ID: {result.import_id}")
    print(f"Message: {result.message}")
    
    if result.errors:
        print(f"\n⚠️  Errors ({len(result.errors)}):")
        for err in result.errors[:5]:  # Show first 5 errors
            print(f"   - Row {err.get('row')}: {err.get('error')}")
    
    # Verify in database
    print("\n🔍 Verifying in database...")
    from app.database import supabase_admin
    
    # Count sales with this import_id
    count_result = supabase_admin.table('sales').select(
        'id', count='exact'
    ).eq('import_id', result.import_id).execute()
    
    db_count = count_result.count if hasattr(count_result, 'count') else len(count_result.data)
    print(f"✅ Found {db_count} records in database with import_id={result.import_id}")
    
    # Check import_history
    history = supabase_admin.table('import_history').select('*').eq(
        'id', result.import_id
    ).execute()
    
    if history.data:
        h = history.data[0]
        print(f"\n📊 Import History:")
        print(f"   Status: {h.get('status')}")
        print(f"   Progress: {h.get('progress_percent')}%")
        print(f"   Total rows: {h.get('total_rows')}")
        print(f"   Imported: {h.get('imported_rows')}")
        print(f"   Failed: {h.get('failed_rows')}")
    
    success = result.success and result.imported_rows == num_rows
    print("\n" + "=" * 80)
    if success:
        print("✅ TEST PASSED - All rows imported successfully!")
    else:
        print(f"❌ TEST FAILED - Expected {num_rows}, got {result.imported_rows}")
    print("=" * 80)
    
    return success

if __name__ == "__main__":
    success = asyncio.run(test_large_import())
    sys.exit(0 if success else 1)
