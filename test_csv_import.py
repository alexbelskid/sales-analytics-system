#!/usr/bin/env python3
"""Test parser with converted CSV"""
import sys
import os
import csv
import asyncio

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.google_sheets_importer import GoogleSheetsImporter
from datetime import date

async def test_import():
    csv_path = "/Users/alexbelski/Downloads/Продажи_TM_converted.csv"
    
    # Read CSV
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        data = list(reader)
    
    print(f"Total rows: {len(data)}")
    
    # Show first 10 rows
    print("\nFirst 10 rows:")
    for i, row in enumerate(data[:10], 1):
        print(f"Row {i}: {row[:5]}")  # First 5 columns
    
    # Initialize importer (without Supabase)
    importer = GoogleSheetsImporter()
    importer.supabase = None  # We don't want to actually save to DB
    
    # Run import logic manually to see what happens
    print("\n" + "="*80)
    print("Running import logic...")
    print("="*80)
    
    # Find header
    header_row_idx = None
    for row_idx, row in enumerate(data):
        if not row or len(row) == 0:
            continue
        first_cell = str(row[0]).strip().upper() if row[0] else ""
        second_cell = str(row[1]).strip().upper() if len(row) > 1 and row[1] else ""
        if ('РЕГИОН' in first_cell or 'ПОЛЬЗОВАТЕЛЬ' in first_cell or
            'РЕГИОН' in second_cell or 'ПОЛЬЗОВАТЕЛЬ' in second_cell):
            header_row_idx = row_idx
            print(f"✅ Found header at row {row_idx}: {row[:3]}")
            break
    
    if header_row_idx is None:
        print("❌ Header not found!")
        return
    
    # Process a few rows after header
    current_region = None
    agents_found = []
    
    for row_idx in range(header_row_idx + 1, min(header_row_idx + 100, len(data))):
        row = data[row_idx]
        if not row or len(row) < 2:
            continue
        
        col_a = str(row[0]).strip() if row[0] else ""
        col_b = str(row[1]).strip() if row[1] else ""
        
        if not col_a and not col_b:
            continue
        
        col_a_upper = col_a.upper()
        
        # Check for region header
        if col_a and not col_b:
            is_region_header = any(region in col_a_upper for region in importer.ALL_REGION_HEADERS)
            if is_region_header:
                current_region = col_a
                print(f"\n📍 Row {row_idx}: REGION = {current_region}")
                continue
        
        # Check for agent
        if col_a and not col_b:
            plan = importer._parse_float(row[2] if len(row) > 2 else None)
            sales = importer._parse_float(row[3] if len(row) > 3 else None)
            
            if plan is not None or sales is not None:
                print(f"   👤 Row {row_idx}: Agent '{col_a}' in '{current_region}', plan={plan}, sales={sales}")
                agents_found.append(col_a)
                if len(agents_found) >= 10:
                    break
    
    print(f"\n✅ Found {len(agents_found)} agents in first 100 rows")

if __name__ == '__main__':
    asyncio.run(test_import())
