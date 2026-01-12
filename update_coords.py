#!/usr/bin/env python3
"""Update customers with region coordinates"""
from supabase import create_client

SUPABASE_URL = "https://hnunemnxpmyhexzcvmtb.supabase.co"
SUPABASE_SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhudW5lbW54cG15aGV4emN2bXRiIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NzEwODc2MSwiZXhwIjoyMDgyNjg0NzYxfQ.4h9QTjZ1YrAH0_k8yB-TF_XLy_JfwaU8wHdiOloKrlo"

supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

REGION_COORDS = {
    "Минск": (53.9045, 27.5615),
    "Брест": (52.0976, 23.6877),
    "Гродно": (53.6884, 23.8258),
    "Витебск": (55.1904, 30.2049),
    "Могилёв": (53.9168, 30.3449),
    "Гомель": (52.4345, 30.9754),
}

def main():
    print("🚀 Updating customers with coordinates...")
    
    customers = supabase.table("customers").select("id, region").execute()
    print(f"   Found {len(customers.data)} customers")
    
    updated = 0
    for c in customers.data:
        region = c.get("region")
        if region and region in REGION_COORDS:
            lat, lon = REGION_COORDS[region]
            supabase.table("customers").update({
                "latitude": lat,
                "longitude": lon
            }).eq("id", c["id"]).execute()
            updated += 1
    
    print(f"✅ Updated {updated} customers with coordinates")

if __name__ == "__main__":
    main()
