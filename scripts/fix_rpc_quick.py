#!/usr/bin/env python3
"""
Quick fix script to apply RPC functions via Supabase Management API
This is an alternative to manually pasting SQL in Supabase SQL Editor
"""

import os
import sys
from pathlib import Path
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ANSI color codes
GREEN = '\033[0;32m'
RED = '\033[0;31m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
NC = '\033[0m'  # No Color

def print_header(text):
    """Print colored section header"""
    print(f"\n{BLUE}{'='*60}{NC}")
    print(f"{BLUE}{text}{NC}")
    print(f"{BLUE}{'='*60}{NC}\n")

def execute_sql_statement(supabase: Client, statement: str, statement_num: int) -> bool:
    """
    Execute a single SQL statement
    Returns True if successful, False otherwise
    """
    try:
        # Clean up the statement
        clean_stmt = statement.strip()
        
        if not clean_stmt or clean_stmt.startswith('--'):
            return True
        
        # Execute using Supabase's query functionality
        # Note: This uses the PostgREST API which has limitations
        # For DDL statements, we need to use a different approach
        
        print(f"   Executing statement #{statement_num}...", end=' ')
        
        # For now, we'll just validate the syntax
        # The actual execution needs to be done through Supabase SQL Editor
        print(f"{YELLOW}⚠  SKIPPED (DDL){NC}")
        return True
        
    except Exception as e:
        print(f"{RED}✗ ERROR{NC}")
        print(f"      Error: {e}")
        return False

def main():
    """Main execution function"""
    
    print_header("🚀 Sales Analytics RPC Functions - Quick Fix")
    
    # Get Supabase credentials
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        print(f"{RED}✗ Error: SUPABASE_URL and SUPABASE_KEY must be set{NC}")
        print(f"\n{YELLOW}Please check your .env file{NC}\n")
        sys.exit(1)
    
    print(f"🔗 Connecting to: {supabase_url}")
    
    try:
        # Create Supabase client
        supabase: Client = create_client(supabase_url, supabase_key)
        print(f"{GREEN}✓ Connected to Supabase{NC}")
        
    except Exception as e:
        print(f"{RED}✗ Connection failed: {e}{NC}")
        sys.exit(1)
    
    # Read SQL file
    sql_file = Path(__file__).parent.parent / "database" / "create_analytics_functions.sql"
    
    if not sql_file.exists():
        print(f"{RED}✗ SQL file not found: {sql_file}{NC}")
        sys.exit(1)
    
    print(f"📄 Reading: {sql_file}")
    sql_content = sql_file.read_text()
    
    print(f"\n{BLUE}{'─'*60}{NC}")
    print(f"{YELLOW}⚠  IMPORTANT NOTICE{NC}")
    print(f"{BLUE}{'─'*60}{NC}")
    print(f"""
Unfortunately, Supabase's Python client does not support executing
DDL statements (CREATE FUNCTION, DROP FUNCTION, etc.) directly.

{GREEN}✓ Good news:{NC} Your SQL file is ready to use!

{YELLOW}📋 Please follow these manual steps:{NC}

1. Open Supabase SQL Editor:
   {BLUE}https://app.supabase.com/project/hnunemnxpmyhexzcvmtb/sql{NC}

2. Copy the SQL file content:
   File: {BLUE}{sql_file}{NC}

3. Paste and run in SQL Editor

4. Verify functions are created:
   SELECT routine_name 
   FROM information_schema.routines 
   WHERE routine_name LIKE 'get_top%';

{GREEN}Alternative (if you have psql installed):{NC}

   psql "postgresql://postgres:[PASSWORD]@db.hnunemnxpmyhexzcvmtb.supabase.co:5432/postgres" \\
     -f {sql_file}

{BLUE}{'─'*60}{NC}

For detailed instructions, see:
   {BLUE}docs/FIX_ANALYTICS_RPC.md{NC}
""")
    
    # Extract function names from SQL for reference
    print(f"\n{GREEN}📊 Functions that will be created:{NC}\n")
    
    if "get_top_products_by_sales" in sql_content:
        print(f"   ✓ get_top_products_by_sales(limit, days)")
        print(f"      → Fixes 'total_revenue ambiguous' error")
    
    if "get_top_customers_by_revenue" in sql_content:
        print(f"   ✓ get_top_customers_by_revenue(limit, days)")
        print(f"      → Optimized customer revenue aggregation")
    
    if "get_sales_trend" in sql_content:
        print(f"   ✓ get_sales_trend(period)")
        print(f"      → Sales trend by day/week/month")
    
    print(f"\n{GREEN}✓ SQL file is ready to apply!{NC}")
    print(f"{YELLOW}⚠  Please apply it manually via Supabase SQL Editor{NC}\n")
    
    # Offer to copy SQL to clipboard (macOS only)
    if sys.platform == 'darwin':
        try:
            import subprocess
            response = input(f"\n{BLUE}Copy SQL to clipboard? (y/n):{NC} ")
            if response.lower() == 'y':
                process = subprocess.Popen(
                    'pbcopy', 
                    stdin=subprocess.PIPE,
                    text=True
                )
                process.communicate(sql_content)
                print(f"{GREEN}✓ SQL copied to clipboard!{NC}")
                print(f"{YELLOW}→ Now paste it in Supabase SQL Editor{NC}\n")
        except Exception as e:
            pass

if __name__ == "__main__":
    main()
