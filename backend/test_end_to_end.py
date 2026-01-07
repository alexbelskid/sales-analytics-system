#!/usr/bin/env python3
"""
END-TO-END IMPORT TEST
Tests the complete import pipeline locally
"""

import sys
import os
import asyncio

sys.path.insert(0, '/Users/alexbelski/Desktop/new bi project/backend')

async def test_full_import_locally():
    print("=" * 70)
    print("🧪 END-TO-END IMPORT TEST")
    print("=" * 70)
    
    file_path = "/Users/alexbelski/Desktop/sales testt.xlsx"
    
    # Test 1: Parser
    print("\n[1] Testing Parser...")
    from app.services.excel_parser import ExcelParser
    parser = ExcelParser(file_path, chunk_size=100)
    total_rows = parser.count_rows()
    print(f"   ✅ Total rows: {total_rows}")
    
    # Parse first chunk
    first_chunk = []
    for chunk in parser.parse_chunks():
        first_chunk = chunk
        break
    
    if first_chunk:
        print(f"   ✅ Parsed first chunk: {len(first_chunk)} rows")
        sample = first_chunk[0]
        print(f"   Sample row keys: {list(sample.keys())}")
        print(f"   Sample: {sample}")
    
    # Test 2: Database import simulation
    print("\n[2] Testing Database Operations...")
    from app.database import get_supabase_admin
    db = get_supabase_admin()
    
    if not db:
        print("   ❌ No database connection")
        return
    
    print("   ✅ Database connected")
    
    # Test 3: Check table existence
    print("\n[3] Checking Tables...")
    tables = ['sales', 'customers', 'products', 'stores', 'import_history']
    for table in tables:
        try:
            result = db.table(table).select('id').limit(1).execute()
            print(f"   ✅ {table}: exists")
        except Exception as e:
            print(f"   ❌ {table}: {str(e)[:100]}")
    
    # Test 4: Try inserting sample data
    print("\n[4] Testing Sample Insert...")
    row = first_chunk[0]
    
    try:
        # Insert customer
        customer_result = db.table('customers').insert({
            'name': row['customer_raw'][:100],
            'normalized_name': row['customer_name'][:100]
        }).execute()
        customer_id = customer_result.data[0]['id']
        print(f"   ✅ Customer inserted: {customer_id}")
        
        # Insert product
        product_result = db.table('products').insert({
            'name': row['product_raw'][:200],
            'normalized_name': row['product_name'][:200],
            'category': (row.get('category') or 'Test')[:100]
        }).execute()
        product_id = product_result.data[0]['id']
        print(f"   ✅ Product inserted: {product_id}")
        
        # Insert sale
        sale_payload = {
            'sale_date': row['sale_date'].isoformat(),
            'customer_id': customer_id,
            'product_id': product_id,
            'store_id': None,
            'total_amount': row['amount'],  # CHECK: using 'amount' from parser
            'quantity': row['quantity'],
            'year': row['year'],
            'month': row['month'],
            'week': row['week'],
            'day_of_week': row['day_of_week']
        }
        print(f"   Sale payload: {sale_payload}")
        
        sale_result = db.table('sales').insert(sale_payload).execute()
        sale_id = sale_result.data[0]['id']
        print(f"   ✅ Sale inserted: {sale_id}")
        
        # Cleanup
        db.table('sales').delete().eq('id', sale_id).execute()
        db.table('customers').delete().eq('id', customer_id).execute()
        db.table('products').delete().eq('id', product_id).execute()
        print(f"   ✅ Cleanup done")
        
    except Exception as e:
        print(f"   ❌ Insert failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 70)
    print("✅ END-TO-END TEST COMPLETE")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(test_full_import_locally())
