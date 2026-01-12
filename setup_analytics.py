#!/usr/bin/env python3
"""
Setup Advanced Analytics - Execute migration against Supabase
Simplified version - only updates existing columns
"""
from supabase import create_client

SUPABASE_URL = "https://hnunemnxpmyhexzcvmtb.supabase.co"
SUPABASE_SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhudW5lbW54cG15aGV4emN2bXRiIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NzEwODc2MSwiZXhwIjoyMDgyNjg0NzYxfQ.4h9QTjZ1YrAH0_k8yB-TF_XLy_JfwaU8wHdiOloKrlo"

supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

REGIONS = ["Минск", "Брест", "Гродно", "Витебск", "Могилёв", "Гомель"]
CATEGORIES = ["Электроника", "Бытовая техника", "Одежда", "Продукты питания", "Товары для дома"]
AGENTS = ["Иванов Александр", "Петрова Мария", "Сидоров Дмитрий", "Козлова Анна", "Новиков Сергей"]

def main():
    print("🚀 Starting Advanced Analytics Setup...")
    
    # 1. Get existing customers  
    print("\n📊 Checking customers...")
    customers = supabase.table("customers").select("*").execute()
    print(f"   Found {len(customers.data)} customers")
    
    # 2. Update customers with regions (only region field)
    if customers.data:
        print("   Updating customers with regions...")
        for i, customer in enumerate(customers.data):
            region = REGIONS[i % len(REGIONS)]
            try:
                supabase.table("customers").update({
                    "region": region
                }).eq("id", customer["id"]).execute()
            except Exception as e:
                print(f"   ⚠️ Could not update customer {customer['id']}: {e}")
                break
        else:
            print(f"   ✅ Updated {len(customers.data)} customers with regions")
    
    # 3. Get existing products
    print("\n📦 Checking products...")
    products = supabase.table("products").select("*").execute()
    print(f"   Found {len(products.data)} products")
    
    # 4. Update products with categories
    if products.data:
        print("   Updating products with categories...")
        for i, product in enumerate(products.data):
            category = CATEGORIES[i % len(CATEGORIES)]
            try:
                supabase.table("products").update({
                    "category": category
                }).eq("id", product["id"]).execute()
            except Exception as e:
                print(f"   ⚠️ Could not update product: {e}")
                break
        else:
            print(f"   ✅ Updated {len(products.data)} products with categories")
    
    # 5. Get existing sales
    print("\n💰 Checking sales...")
    sales = supabase.table("sales").select("id").limit(500).execute()
    print(f"   Found {len(sales.data)} sales (limited to 500)")
    
    # 6. Update sales with agent names
    if sales.data:
        print("   Updating sales with agent names...")
        updated = 0
        for i, sale in enumerate(sales.data):
            agent = AGENTS[i % len(AGENTS)]
            try:
                supabase.table("sales").update({
                    "agent_name": agent
                }).eq("id", sale["id"]).execute()
                updated += 1
            except Exception as e:
                if "agent_name" in str(e):
                    print(f"   ⚠️ agent_name column doesn't exist, skipping...")
                    break
                else:
                    print(f"   ⚠️ Error: {e}")
                    break
        if updated > 0:
            print(f"   ✅ Updated {updated} sales with agent names")
    
    # 7. Sales plans
    print("\n📋 Setting up sales plans...")
    from datetime import date, timedelta
    today = date.today()
    current_month = today.replace(day=1)
    last_month = (current_month - timedelta(days=1)).replace(day=1)
    
    try:
        supabase.table("sales_plans").insert({
            "period": str(current_month),
            "planned_amount": 1500000,
            "planned_quantity": 750
        }).execute()
        
        supabase.table("sales_plans").insert({
            "period": str(last_month),
            "planned_amount": 1200000,
            "planned_quantity": 600
        }).execute()
        print("   ✅ Sales plans created")
    except Exception as e:
        if "duplicate" in str(e).lower():
            print("   ℹ️ Sales plans already exist")
        else:
            print(f"   ⚠️ Could not create sales_plans: {e}")
    
    print("\n✅ Setup complete!")
    
    # Test API
    print("\n📈 Testing API endpoints...")
    import requests
    API_URL = "https://athletic-alignment-production-db41.up.railway.app"
    
    endpoints = [
        "/api/analytics/filter-options",
        "/api/analytics/abc-xyz?days=365",
        "/api/analytics/geo?days=365",
    ]
    
    for ep in endpoints:
        try:
            r = requests.get(f"{API_URL}{ep}", timeout=10)
            data = r.json()
            print(f"   {ep}: {r.status_code}")
            if ep == "/api/analytics/filter-options":
                print(f"      regions: {len(data.get('regions', []))}, categories: {len(data.get('categories', []))}")
            elif ep == "/api/analytics/abc-xyz?days=365":
                print(f"      total_products: {data.get('summary', {}).get('total_products', 0)}")
            elif ep == "/api/analytics/geo?days=365":
                print(f"      total_revenue: {data.get('total_revenue', 0)}")
        except Exception as e:
            print(f"   {ep}: Error - {e}")

if __name__ == "__main__":
    main()
