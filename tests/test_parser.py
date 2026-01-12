#!/usr/bin/env python3
"""Test the Google Sheets parser with real CSV data"""
import sys
import os
import csv
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.google_sheets_importer import GoogleSheetsImporter

def test_parser_with_csv():
    csv_path = "/Users/alexbelski/Downloads/test_agent_sales.csv"
    
    print(f"Testing parser with: {csv_path}")
    print("=" * 80)
    
    # Read CSV file
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = list(reader)
    
    print(f"Total rows: {len(rows)}")
    print()
    
    # Initialize importer
    importer = GoogleSheetsImporter()
    
    # Track what we find
    regions_found = []
    agents_found = []
    current_region = None
    
    print("PARSING ANALYSIS:")
    print("=" * 80)
    
    for i, row in enumerate(rows, 1):
        if not row or len(row) < 2:
            continue
            
        # Check if this is a region header
        potential_region = str(row[1]).strip()
        
        # Use the same logic as the parser
        # Check if it's a pure geographic region (not a team)
        is_region_header = (
            potential_region in importer.REGIONS and
            len(row) > 3 and
            (not row[2] or str(row[2]).strip() == '')
        )
        
        if is_region_header:
            current_region = potential_region
            regions_found.append((i, potential_region))
            print(f"\n📍 Line {i}: REGION = {potential_region}")
            
        elif current_region and potential_region and potential_region not in importer.ALL_REGION_HEADERS:
            # This might be an agent
            # Check if it has sales data
            if len(row) > 3 and row[3]:
                try:
                    plan = importer._parse_float(row[3])
                    actual = importer._parse_float(row[4]) if len(row) > 4 else 0
                    if plan > 0 or actual > 0:
                        agents_found.append({
                            'line': i,
                            'region': current_region,
                            'name': potential_region,
                            'plan': plan,
                            'actual': actual
                        })
                        print(f"   👤 Line {i}: Agent '{potential_region}' - Plan: {plan:,.0f}, Actual: {actual:,.0f}")
                except:
                    pass
    
    print("\n" + "=" * 80)
    print("SUMMARY:")
    print("=" * 80)
    print(f"Regions found: {len(regions_found)}")
    for line, region in regions_found:
        print(f"  - Line {line}: {region}")
    
    print(f"\nAgents found: {len(agents_found)}")
    
    # Find Дворник Евгения
    dvornik = [a for a in agents_found if 'Дворник' in a['name']]
    if dvornik:
        print("\n✅ FOUND: Дворник Евгения")
        for agent in dvornik:
            print(f"   Line {agent['line']}")
            print(f"   Region: {agent['region']}")
            print(f"   Plan: {agent['plan']:,.0f} Br")
            print(f"   Actual: {agent['actual']:,.0f} Br")
    else:
        print("\n❌ NOT FOUND: Дворник Евгения")
    
    # Check МОГИЛЕВ region
    mogilev_agents = [a for a in agents_found if a['region'] == 'МОГИЛЕВ']
    print(f"\n📊 МОГИЛЕВ region has {len(mogilev_agents)} agents:")
    for agent in mogilev_agents[:10]:  # Show first 10
        print(f"   - {agent['name']}: {agent['plan']:,.0f} / {agent['actual']:,.0f}")

if __name__ == '__main__':
    test_parser_with_csv()
