#!/usr/bin/env python3
"""
Full parser test - parse ALL rows and verify control sums
"""

import sys
sys.path.insert(0, '/Users/alexbelski/Desktop/new bi project/backend')

from app.services.excel_parser import ExcelParser

def full_test(file_path: str):
    print("=" * 60)
    print("🧪 FULL PARSER TEST - ALL ROWS")
    print("=" * 60)
    
    parser = ExcelParser(file_path, chunk_size=1000)
    
    # Count rows
    total = parser.count_rows()
    print(f"\n📊 Total rows in file: {total}")
    
    # Parse ALL rows
    all_rows = []
    for chunk in parser.parse_chunks():
        all_rows.extend(chunk)
    
    # Stats
    stats = parser.get_stats()
    print(f"\n📊 PARSING RESULTS:")
    print(f"  Total rows:     {stats['total_rows']}")
    print(f"  Processed:      {stats['processed_rows']}")
    print(f"  Failed:         {stats['failed_rows']}")
    print(f"  Success rate:   {stats['success_rate']}%")
    
    # Control sums
    total_amount = sum(r.get('amount', 0) for r in all_rows)
    total_quantity = sum(r.get('quantity', 0) for r in all_rows)
    min_amount = min((r.get('amount', float('inf')) for r in all_rows), default=0)
    max_amount = max((r.get('amount', 0) for r in all_rows), default=0)
    
    print(f"\n💰 CONTROL SUMS (PARSED DATA):")
    print(f"  Total Amount:   {total_amount:,.2f} Br")
    print(f"  Total Quantity: {total_quantity:,.2f}")
    print(f"  Min Amount:     {min_amount:,.2f} Br")
    print(f"  Max Amount:     {max_amount:,.2f} Br")
    print(f"  Rows parsed:    {len(all_rows)}")
    
    print(f"\n📋 EXPECTED (from Excel diagnose):")
    print(f"  Total rows:     128")
    print(f"  Total Amount:   18,539.04 Br")
    print(f"  Min Amount:     9.79 Br")
    print(f"  Max Amount:     3,999.60 Br")
    
    # Compare
    excel_total = 18539.04
    diff = abs(total_amount - excel_total)
    match_pct = 100 - (diff / excel_total * 100) if excel_total > 0 else 0
    
    print(f"\n🔍 COMPARISON:")
    print(f"  Parsed:   {total_amount:,.2f} Br")
    print(f"  Excel:    {excel_total:,.2f} Br")
    print(f"  Match:    {match_pct:.2f}%")
    
    if match_pct >= 99.9:
        print(f"\n✅ CONTROL SUMS MATCH!")
    else:
        print(f"\n⚠️ DIFFERENCE: {diff:,.2f} Br ({100-match_pct:.2f}%)")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    full_test("/Users/alexbelski/Desktop/sales testt.xlsx")
