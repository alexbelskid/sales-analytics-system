#!/usr/bin/env python3
"""
Excel Parser Diagnostic Tool
Analyzes an Excel file and shows column structure + sample data
"""

import sys
import pandas as pd
from pathlib import Path

def analyze_excel(file_path: str):
    """Analyze Excel file structure and content"""
    
    print("=" * 60)
    print("📊 EXCEL FILE ANALYSIS")
    print("=" * 60)
    print(f"\nFile: {file_path}")
    
    # Try to load with different engines
    df = None
    for engine in ['openpyxl', 'calamine', 'xlrd', None]:
        try:
            df = pd.read_excel(file_path, header=0, engine=engine)
            print(f"✅ Loaded successfully with engine: {engine or 'default'}")
            break
        except Exception as e:
            print(f"❌ Engine {engine}: {str(e)[:100]}")
    
    if df is None:
        print("\n❌ FAILED TO LOAD FILE!")
        return
    
    # Basic info
    print(f"\n📋 BASIC INFO:")
    print(f"  Total Rows: {len(df)}")
    print(f"  Total Columns: {len(df.columns)}")
    
    # Column structure
    print(f"\n📌 COLUMN STRUCTURE (0-indexed):")
    print("-" * 60)
    for i, col in enumerate(df.columns):
        sample = df.iloc[0][col] if len(df) > 0 else "N/A"
        sample_str = str(sample)[:50] + "..." if len(str(sample)) > 50 else str(sample)
        print(f"  [{i:2}] {str(col)[:30]:<30} | Sample: {sample_str}")
    print("-" * 60)
    
    # Sample rows
    print(f"\n📝 SAMPLE ROWS (first 3 data rows):")
    for idx in [0, 1, 2]:
        if idx < len(df):
            print(f"\n  --- ROW {idx + 2} (Excel row number) ---")
            for col_idx, col in enumerate(df.columns):
                val = df.iloc[idx][col]
                val_str = str(val)[:60] + "..." if len(str(val)) > 60 else str(val)
                print(f"    Col[{col_idx:2}] {str(col)[:25]:<25}: {val_str}")
    
    # Special check for Amount column (try to find it)
    print(f"\n💰 SEARCHING FOR 'AMOUNT/СУММА' COLUMN:")
    amount_candidates = []
    for i, col in enumerate(df.columns):
        col_str = str(col).lower()
        if 'сумма' in col_str or 'amount' in col_str or 'total' in col_str or 'ндс' in col_str:
            amount_candidates.append((i, col))
            
    if amount_candidates:
        for idx, col in amount_candidates:
            col_sum = pd.to_numeric(df[col], errors='coerce').sum()
            print(f"  [{idx}] '{col}' -> SUM = {col_sum:,.2f}")
    else:
        print("  ⚠️ No obvious amount column found. Checking numeric columns:")
        for i, col in enumerate(df.columns):
            if df[col].dtype in ['int64', 'float64']:
                col_sum = df[col].sum()
                if col_sum > 0:
                    print(f"    [{i}] '{col}' -> SUM = {col_sum:,.2f}")
    
    # Calculate control sums
    print(f"\n📊 CONTROL SUMS:")
    print(f"  Total rows with data: {len(df)}")
    
    # Try to find and sum amount column
    amount_col_idx = 17  # Current config says R (index 17)
    if amount_col_idx < len(df.columns):
        amount_col = df.columns[amount_col_idx]
        try:
            total_amount = pd.to_numeric(df[amount_col], errors='coerce').sum()
            min_amount = pd.to_numeric(df[amount_col], errors='coerce').min()
            max_amount = pd.to_numeric(df[amount_col], errors='coerce').max()
            print(f"  Column [{amount_col_idx}] '{amount_col}':")
            print(f"    Total: {total_amount:,.2f}")
            print(f"    Min: {min_amount:,.2f}")
            print(f"    Max: {max_amount:,.2f}")
        except:
            print(f"  ⚠️ Column [{amount_col_idx}] is not numeric")
    
    # Current parser mapping check
    print(f"\n🔧 CURRENT PARSER MAPPING vs ACTUAL:")
    current_map = {
        'date': 1,           # B: Дата
        'store_code': 3,     # D: Код точки
        'region': 4,         # E: Регион
        'channel': 5,        # F: Канал сбыта
        'store_name': 6,     # G: Город/Точка
        'customer': 8,       # I: Контрагент
        'address': 9,        # J: Адрес
        'category': 11,      # L: Группа товара
        'product_type': 12,  # M: Вид товара
        'product': 13,       # N: Номенклатура
        'barcode': 14,       # O: Штрихкод
        'quantity': 16,      # Q: Количество
        'amount': 17,        # R: Сумма с НДС
    }
    
    print("-" * 60)
    for field, col_idx in current_map.items():
        if col_idx < len(df.columns):
            actual_col = df.columns[col_idx]
            sample = df.iloc[0][actual_col] if len(df) > 0 else "N/A"
            print(f"  {field:15} -> Col[{col_idx:2}] = '{actual_col}' | Sample: {str(sample)[:30]}")
        else:
            print(f"  {field:15} -> Col[{col_idx:2}] = ⚠️ INDEX OUT OF RANGE!")
    print("-" * 60)
    
    print("\n✅ ANALYSIS COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python diagnose_excel.py <path_to_excel_file>")
        print("\nExample:")
        print("  python diagnose_excel.py /path/to/your/sales.xlsx")
        sys.exit(1)
    
    file_path = sys.argv[1]
    if not Path(file_path).exists():
        print(f"❌ File not found: {file_path}")
        sys.exit(1)
    
    analyze_excel(file_path)
