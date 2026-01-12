#!/usr/bin/env python3
"""Convert .xls to .csv"""
import sys
import csv

try:
    import xlrd
    workbook = xlrd.open_workbook('/Users/alexbelski/Downloads/Продажи ТМ 08.01.2026 85022.xls')
    sheet = workbook.sheet_by_index(0)
    
    with open('/Users/alexbelski/Downloads/Продажи_TM_converted.csv', 'w', encoding='utf-8') as f:
        writer = csv.writer(f)
        for row_idx in range(sheet.nrows):
            row_data = []
            for col_idx in range(sheet.ncols):
                cell = sheet.cell(row_idx, col_idx)
                row_data.append(cell.value)
            writer.writerow(row_data)
    
    print("✅ Converted to /Users/alexbelski/Downloads/Продажи_TM_converted.csv")
except ImportError:
    # Try with python-calamine
    from python_calamine import CalamineWorkbook
    import io
    
    with open('/Users/alexbelski/Downloads/Продажи ТМ 08.01.2026 85022.xls', 'rb') as f:
        workbook = CalamineWorkbook.from_filelike(io.BytesIO(f.read()))
    
    sheet_names = workbook.sheet_names
    rows = workbook.get_sheet_by_name(sheet_names[0]).to_python()
    
    with open('/Users/alexbelski/Downloads/Продажи_TM_converted.csv', 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(rows)
    
    print("✅ Converted to /Users/alexbelski/Downloads/Продажи_TM_converted.csv")
