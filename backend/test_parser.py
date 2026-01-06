#!/usr/bin/env python3
"""
Test the fixed Excel parser on sample file
"""

import sys
sys.path.insert(0, '/Users/alexbelski/Desktop/new bi project/backend')

from app.services.excel_parser import ExcelParser

def test_parser(file_path: str):
    print("=" * 60)
    print("🧪 TESTING FIXED PARSER")
    print("=" * 60)
    
    parser = ExcelParser(file_path, chunk_size=50)
    
    # Count rows
    total = parser.count_rows()
    print(f"\n📊 Total rows: {total}")
    
    # Parse first chunk
    print("\n📝 PARSING FIRST 10 ROWS:")
    print("-" * 60)
    
    parsed_rows = []
    for chunk in parser.parse_chunks():
        parsed_rows.extend(chunk)
        if len(parsed_rows) >= 10:
            break
    
    # Show first 5 parsed rows
    for i, row in enumerate(parsed_rows[:5]):
        print(f"\n--- Row {i+1} ---")
        print(f"  Date:      {row.get('sale_date')}")
        print(f"  Customer:  {row.get('customer_raw', '')[:50]}")
        print(f"  Product:   {row.get('product_raw', '')[:50]}")
        print(f"  Quantity:  {row.get('quantity')}")
        print(f"  Amount:    {row.get('amount')}")
        print(f"  Category:  {row.get('category')}")
        print(f"  Region:    {row.get('region')}")
        print(f"  Channel:   {row.get('channel')}")
    
    # Stats
    stats = parser.get_stats()
    print(f"\n📊 PARSING STATS:")
    print(f"  Total rows:     {stats['total_rows']}")
    print(f"  Processed:      {stats['processed_rows']}")
    print(f"  Failed:         {stats['failed_rows']}")
    print(f"  Success rate:   {stats['success_rate']}%")
    
    if stats['errors']:
        print(f"\n⚠️ ERRORS (first 5):")
        for err in stats['errors'][:5]:
            print(f"    {err}")
    
    # Calculate total amount
    if parsed_rows:
        total_amount = sum(r.get('amount', 0) for r in parsed_rows)
        print(f"\n💰 Total amount from parsed rows: {total_amount:.2f} Br")
    
    print("\n✅ TEST COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    test_parser("/Users/alexbelski/Desktop/sales testt.xlsx")
