#!/usr/bin/env python3
"""Download Google Sheet as CSV for testing"""
import requests

# Google Sheets URL (use export format)
SHEET_ID = "1tuyVZmkbe4pAAaKdKdetASFaCKh3Iskl_N00MsSfzto"
GID = "2146429336"  # TDSheet tab

# Export URL
export_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID}"

print(f"Downloading from: {export_url}")

response = requests.get(export_url)
if response.status_code == 200:
    output_path = "/Users/alexbelski/Downloads/test_agent_sales.csv"
    with open(output_path, 'wb') as f:
        f.write(response.content)
    print(f"✅ Downloaded to: {output_path}")
    
    # Print first few lines
    print("\nFirst 20 lines:")
    print("=" * 80)
    lines = response.content.decode('utf-8').split('\n')
    for i, line in enumerate(lines[:20], 1):
        print(f"{i:3}: {line[:100]}")
else:
    print(f"❌ Error: {response.status_code}")
