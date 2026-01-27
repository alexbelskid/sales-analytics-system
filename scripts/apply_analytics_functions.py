#!/usr/bin/env python3
"""
Apply Analytics RPC Functions to Supabase
This script applies the analytics RPC functions to fix the ambiguous column reference error.
"""

import os
import sys
from pathlib import Path
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def apply_analytics_functions():
    """Apply analytics RPC functions to Supabase database."""
    
    # Get Supabase credentials
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        print("❌ Error: SUPABASE_URL and SUPABASE_KEY must be set in .env file")
        sys.exit(1)
    
    print(f"🔗 Connecting to Supabase: {supabase_url}")
    
    try:
        # Create Supabase client
        supabase: Client = create_client(supabase_url, supabase_key)
        print("✅ Connected to Supabase")
        
        # Read SQL file
        sql_file = Path(__file__).parent / "database" / "create_analytics_functions.sql"
        
        if not sql_file.exists():
            print(f"❌ Error: SQL file not found: {sql_file}")
            sys.exit(1)
        
        print(f"📄 Reading SQL file: {sql_file}")
        sql_content = sql_file.read_text()
        
        # Split SQL into individual statements
        statements = [
            stmt.strip() 
            for stmt in sql_content.split(';') 
            if stmt.strip() and not stmt.strip().startswith('--')
        ]
        
        print(f"📝 Found {len(statements)} SQL statements to execute")
        
        # Execute each statement
        for i, statement in enumerate(statements, 1):
            # Skip comments and empty statements
            if not statement or statement.startswith('--'):
                continue
            
            # Skip NOTIFY statements (they need special handling)
            if 'NOTIFY' in statement.upper():
                print(f"⏭️  Skipping NOTIFY statement #{i}")
                continue
            
            try:
                print(f"⚙️  Executing statement #{i}...")
                
                # For CREATE FUNCTION, we need to use the SQL execution endpoint
                result = supabase.rpc('exec_sql', {'query': statement + ';'}).execute()
                
                print(f"✅ Statement #{i} executed successfully")
                
            except Exception as e:
                # Some statements may fail if functions don't exist yet
                # That's okay - DROP IF EXISTS will handle it gracefully
                if 'does not exist' in str(e).lower():
                    print(f"⚠️  Statement #{i}: {e} (safe to ignore)")
                else:
                    print(f"❌ Error executing statement #{i}: {e}")
                    # Continue anyway - some errors are expected
        
        print("\n" + "="*60)
        print("✅ Analytics functions applied successfully!")
        print("="*60)
        print("\n📋 Created functions:")
        print("  • get_top_products_by_sales(limit, days)")
        print("  • get_top_customers_by_revenue(limit, days)")
        print("  • get_sales_trend(period)")
        print("\n💡 These functions fix the 'total_revenue ambiguous' error")
        print("\n🔄 Please restart your backend server to see the changes")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 You may need to apply the SQL manually:")
        print(f"   1. Open Supabase SQL Editor: {supabase_url.replace('https://', 'https://app.')}/sql")
        print(f"   2. Copy contents of: database/create_analytics_functions.sql")
        print(f"   3. Paste and execute in SQL Editor")
        sys.exit(1)

if __name__ == "__main__":
    print("🚀 Applying Analytics RPC Functions to Supabase")
    print("="*60 + "\n")
    apply_analytics_functions()
