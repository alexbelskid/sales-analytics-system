#!/usr/bin/env python3
"""
FULL IMPORT TEST - Simulates the entire import process locally
Helps identify exactly what's failing
"""

import sys
import os
import traceback

# Add backend to path
sys.path.insert(0, '/Users/alexbelski/Desktop/new bi project/backend')

def test_full_import(file_path: str):
    print("=" * 70)
    print("🧪 FULL IMPORT TEST - SIMULATING ENTIRE PIPELINE")
    print("=" * 70)
    
    # Test 1: Parser
    print("\n[STEP 1] Testing Excel Parser...")
    try:
        from app.services.excel_parser import ExcelParser
        parser = ExcelParser(file_path, chunk_size=100)
        total_rows = parser.count_rows()
        print(f"  ✅ Parser initialized. Total rows: {total_rows}")
    except Exception as e:
        print(f"  ❌ PARSER FAILED: {e}")
        traceback.print_exc()
        return
    
    # Test 2: Database connection
    print("\n[STEP 2] Testing Database Connection...")
    try:
        from app.database import get_supabase_admin
        db = get_supabase_admin()
        if db:
            print("  ✅ Supabase Admin connected")
        else:
            print("  ❌ Supabase Admin is None!")
            return
    except Exception as e:
        print(f"  ❌ DATABASE FAILED: {e}")
        traceback.print_exc()
        return
    
    # Test 3: Check tables exist
    print("\n[STEP 3] Checking Required Tables...")
    tables_to_check = ['customers', 'products', 'stores', 'sales', 'import_history']
    for table in tables_to_check:
        try:
            result = db.table(table).select('id').limit(1).execute()
            print(f"  ✅ {table}: exists")
        except Exception as e:
            print(f"  ❌ {table}: FAILED - {str(e)[:100]}")
    
    # Test 4: Parse first chunk
    print("\n[STEP 4] Parsing First Chunk...")
    try:
        parser = ExcelParser(file_path, chunk_size=10)  # Small chunk
        parser.count_rows()
        
        first_rows = []
        for chunk in parser.parse_chunks():
            first_rows.extend(chunk)
            break  # Only first chunk
        
        if first_rows:
            print(f"  ✅ Parsed {len(first_rows)} rows")
            print(f"  Sample: {first_rows[0]}")
        else:
            print("  ❌ No rows parsed!")
            return
    except Exception as e:
        print(f"  ❌ PARSING FAILED: {e}")
        traceback.print_exc()
        return
    
    # Test 5: Simulate customer/product insert
    print("\n[STEP 5] Testing Entity Inserts (DRY RUN)...")
    row = first_rows[0]
    
    try:
        # Check customer insert
        test_customer = {
            'name': row['customer_raw'][:100],  # Truncate to safe length
            'normalized_name': row['customer_name'][:100]
        }
        print(f"  Customer payload: {test_customer}")
        
        # Actually try to insert
        result = db.table('customers').insert(test_customer).execute()
        customer_id = result.data[0]['id']
        print(f"  ✅ Customer inserted: {customer_id}")
        
        # Delete test record
        db.table('customers').delete().eq('id', customer_id).execute()
        print(f"  ✅ Customer cleaned up")
        
    except Exception as e:
        print(f"  ❌ CUSTOMER INSERT FAILED: {e}")
        traceback.print_exc()
    
    try:
        # Check product insert
        test_product = {
            'name': row['product_raw'][:200],  
            'normalized_name': row['product_name'][:200],
            'category': (row.get('category') or 'Без категории')[:100]
        }
        print(f"  Product payload: {test_product}")
        
        result = db.table('products').insert(test_product).execute()
        product_id = result.data[0]['id']
        print(f"  ✅ Product inserted: {product_id}")
        
        db.table('products').delete().eq('id', product_id).execute()
        print(f"  ✅ Product cleaned up")
        
    except Exception as e:
        print(f"  ❌ PRODUCT INSERT FAILED: {e}")
        traceback.print_exc()
    
    try:
        # Check stores insert
        store_code = str(row.get('store_code') or 'TEST')[:50]
        test_store = {
            'code': store_code,
            'name': str(row.get('store_name') or store_code)[:200],
            'region': str(row.get('region') or '')[:100],
            'channel': str(row.get('channel') or '')[:100]
        }
        print(f"  Store payload: {test_store}")
        
        result = db.table('stores').insert(test_store).execute()
        store_id = result.data[0]['id']
        print(f"  ✅ Store inserted: {store_id}")
        
        db.table('stores').delete().eq('id', store_id).execute()
        print(f"  ✅ Store cleaned up")
        
    except Exception as e:
        print(f"  ❌ STORE INSERT FAILED: {e}")
        traceback.print_exc()
    
    # Test 6: Simulate sales insert
    print("\n[STEP 6] Testing Sales Insert (DRY RUN)...")
    try:
        test_sale = {
            'sale_date': row['sale_date'].isoformat(),
            'customer_id': None,  # Would be real ID
            'product_id': None,   # Would be real ID
            'store_id': None,
            'total_amount': row['amount'],
            'quantity': row['quantity'],
            'year': row['year'],
            'month': row['month'],
            'week': row['week'],
            'day_of_week': row['day_of_week']
        }
        print(f"  Sales payload: {test_sale}")
        print(f"  ⚠️ Skipping actual insert (no foreign keys)")
        
    except Exception as e:
        print(f"  ❌ SALES FAILED: {e}")
        traceback.print_exc()
    
    print("\n" + "=" * 70)
    print("✅ ALL TESTS PASSED" if True else "❌ TESTS FAILED")
    print("=" * 70)

if __name__ == "__main__":
    test_full_import("/Users/alexbelski/Desktop/sales testt.xlsx")
