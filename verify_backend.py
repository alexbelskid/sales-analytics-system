
import requests
import json
import sys

BASE_URL = "http://localhost:8000"

def test_endpoint(method, url, data=None):
    try:
        full_url = f"{BASE_URL}{url}"
        print(f"Testing {method} {url}...", end=" ")
        
        if method == "GET":
            response = requests.get(full_url)
        elif method == "POST":
            response = requests.post(full_url, json=data)
            
        if response.status_code in [200, 201]:
            print(f"✅ OK ({response.status_code})")
            return True, response.json()
        elif response.status_code == 404:
             print(f"❌ NOT FOUND ({response.status_code})")
             return False, None
        else:
            print(f"⚠️ {response.status_code}")
            # print(response.text)
            return False, response.text
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False, str(e)

print("--- SALES ANALYTICS BACKEND CHECK ---")

print("\n1. Checking Core Analytics Endpoints:")
test_endpoint("GET", "/api/analytics/dashboard")
test_endpoint("GET", "/api/analytics/sales-trend")
test_endpoint("GET", "/api/analytics/plan-fact?period_start=2025-01-01&period_end=2025-01-31")

print("\n2. Checking Advanced Analytics (New):")
test_endpoint("GET", "/api/analytics/abc-xyz?days=90")
test_endpoint("POST", "/api/analytics/what-if", {
    "price_change_pct": 10,
    "volume_change_pct": -5, 
    "cost_change_pct": 0,
    "new_customers_pct": 0
})

print("\n3. Checking AI Endpoints:")
test_endpoint("GET", "/api/ai/status")
# We won't trigger generation to save credits/time, just status check

print("\n4. Checking Import Endpoints:")
test_endpoint("GET", "/api/import/types")

print("\n-------------------------------------")
