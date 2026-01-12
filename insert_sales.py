#!/usr/bin/env python3
"""Insert test sales data directly into Supabase - simplified version"""
from supabase import create_client
from datetime import date, timedelta
import random

SUPABASE_URL = "https://hnunemnxpmyhexzcvmtb.supabase.co"
SUPABASE_SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhudW5lbW54cG15aGV4emN2bXRiIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NzEwODc2MSwiZXhwIjoyMDgyNjg0NzYxfQ.4h9QTjZ1YrAH0_k8yB-TF_XLy_JfwaU8wHdiOloKrlo"

supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

def main():
    print("🚀 Loading test sales data...")
    
    # Get existing customers
    customers = supabase.table("customers").select("id, name").execute()
    print(f"   Found {len(customers.data)} customers")
    
    # Get existing products
    products = supabase.table("products").select("id, name").execute()
    print(f"   Found {len(products.data)} products")
    
    if not customers.data:
        print("❌ No customers found!")
        return
    
    # Generate 100 sales over last 90 days
    agents = ["Иванов Александр", "Петрова Мария", "Сидоров Дмитрий", "Козлова Анна", "Новиков Сергей"]
    
    inserted = 0
    for i in range(100):
        customer = random.choice(customers.data)
        agent = random.choice(agents)
        
        days_ago = random.randint(1, 90)
        sale_date_obj = date.today() - timedelta(days=days_ago)
        sale_date = sale_date_obj.isoformat()
        sale_year = sale_date_obj.year
        sale_month = sale_date_obj.month
        
        quantity = random.randint(1, 5)
        price = random.randint(5000, 80000)
        total = quantity * price
        
        try:
            # Insert sale only (without sale_items)
            sale = supabase.table("sales").insert({
                "customer_id": customer["id"],
                "sale_date": sale_date,
                "total_amount": total,
                "agent_name": agent,
                "year": sale_year,
                "month": sale_month,
                "quantity": quantity,
            }).execute()
            
            inserted += 1
            if inserted % 20 == 0:
                print(f"   Inserted {inserted} sales...")
        except Exception as e:
            print(f"   ⚠️ Error: {e}")
            break
    
    print(f"\n✅ Inserted {inserted} sales!")
    
    # Verify
    sales = supabase.table("sales").select("id").execute()
    print(f"   Total sales in DB: {len(sales.data)}")

if __name__ == "__main__":
    main()
