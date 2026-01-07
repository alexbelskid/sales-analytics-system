#!/usr/bin/env python3
"""
Test file upload to Railway
"""

import requests

API_URL = "https://athletic-alignment-production-db41.up.railway.app"
file_path = "/Users/alexbelski/Desktop/sales testt.xlsx"

print(f"Uploading {file_path} to {API_URL}...")

with open(file_path, 'rb') as f:
    files = {'file': (file_path.split('/')[-1], f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
    
    response = requests.post(
        f"{API_URL}/api/import/upload-excel",
        files=files,
        timeout=30
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")

# Check file list
print("\nChecking file list...")
response = requests.get(f"{API_URL}/api/files/list", timeout=10)
print(f"Files: {response.json()}")
