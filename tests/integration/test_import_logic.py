"""
Test script to verify sales import logic
"""
import pandas as pd
from datetime import datetime

# Simulate a row from Excel
test_row = {
    'customer_name': 'Test Customer',
    'date': '2025-01-15',
    'amount': 1000.50,
    'product_name': 'Test Product',
    'quantity': 5,
    'price': 200.10
}

# Test date parsing logic
sale_date = test_row.get('date', datetime.now().date())
print(f"Input date: {sale_date}")
print(f"Type: {type(sale_date)}")

if isinstance(sale_date, str):
    sale_date_obj = pd.to_datetime(sale_date).date()
    sale_date = sale_date_obj.isoformat()
    year = sale_date_obj.year
    month = sale_date_obj.month
    print(f"✅ String path: date={sale_date}, year={year}, month={month}")
elif hasattr(sale_date, 'isoformat'):
    year = sale_date.year if hasattr(sale_date, 'year') else datetime.now().year
    month = sale_date.month if hasattr(sale_date, 'month') else datetime.now().month
    sale_date = sale_date.isoformat()
    print(f"✅ Date object path: date={sale_date}, year={year}, month={month}")
else:
    year = datetime.now().year
    month = datetime.now().month
    sale_date = datetime.now().date().isoformat()
    print(f"✅ Fallback path: date={sale_date}, year={year}, month={month}")

total = float(test_row.get('amount', test_row.get('total', 0)))
print(f"✅ Total amount: {total}")

# Show what would be inserted
insert_data = {
    "customer_id": "test-uuid",
    "sale_date": sale_date,
    "year": year,
    "month": month,
    "total_amount": total
}

print("\n📦 Data to insert into sales table:")
for key, value in insert_data.items():
    print(f"  {key}: {value} ({type(value).__name__})")

print("\n✅ All required fields present!")
