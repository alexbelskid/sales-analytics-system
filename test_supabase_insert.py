"""
Test script to directly insert into Supabase and see exact error
"""
import os
from datetime import datetime
import pandas as pd
from supabase import create_client

# Initialize Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Missing SUPABASE_URL or SUPABASE_SERVICE_KEY environment variables")
    exit(1)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

print("✅ Connected to Supabase")

# Test data
test_row = {
    'customer_name': 'Test Customer',
    'date': '2025-01-15',
    'amount': 1000.50
}

try:
    # Step 1: Create customer
    print("\n📝 Step 1: Creating customer...")
    customer_name = str(test_row.get('customer_name', 'Unknown'))
    normalized_name = customer_name.lower().strip()
    
    customer_result = supabase.table("customers").select("id").eq("name", customer_name).execute()
    
    if customer_result.data:
        customer_id = customer_result.data[0]["id"]
        print(f"✅ Customer exists: {customer_id}")
    else:
        new_customer = supabase.table("customers").insert({
            "name": customer_name,
            "normalized_name": normalized_name
        }).execute()
        customer_id = new_customer.data[0]["id"]
        print(f"✅ Customer created: {customer_id}")
    
    # Step 2: Parse date
    print("\n📝 Step 2: Parsing date...")
    sale_date = test_row.get('date', datetime.now().date())
    if isinstance(sale_date, str):
        sale_date_obj = pd.to_datetime(sale_date).date()
        sale_date = sale_date_obj.isoformat()
        year = sale_date_obj.year
        month = sale_date_obj.month
    elif hasattr(sale_date, 'isoformat'):
        year = sale_date.year if hasattr(sale_date, 'year') else datetime.now().year
        month = sale_date.month if hasattr(sale_date, 'month') else datetime.now().month
        sale_date = sale_date.isoformat()
    else:
        year = datetime.now().year
        month = datetime.now().month
        sale_date = datetime.now().date().isoformat()
    
    print(f"✅ Parsed: date={sale_date}, year={year}, month={month}")
    
    total = float(test_row.get('amount', test_row.get('total', 0)))
    print(f"✅ Total: {total}")
    
    # Step 3: Insert sale
    print("\n📝 Step 3: Inserting sale...")
    sale_data = {
        "customer_id": customer_id,
        "sale_date": sale_date,
        "year": year,
        "month": month,
        "total_amount": total
    }
    
    print(f"Data to insert: {sale_data}")
    
    sale = supabase.table("sales").insert(sale_data).execute()
    
    print(f"✅ Sale created: {sale.data[0]['id']}")
    print("\n🎉 SUCCESS! All fields are correct!")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    print(f"\nError type: {type(e).__name__}")
    if hasattr(e, 'message'):
        print(f"Message: {e.message}")
    if hasattr(e, 'details'):
        print(f"Details: {e.details}")
    
    import traceback
    print("\nFull traceback:")
    traceback.print_exc()
