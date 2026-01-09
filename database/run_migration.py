import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Error: SUPABASE_URL and SUPABASE_KEY must be set in .env")
    exit(1)

# Create Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Read migration SQL
with open("database/migrations/003_create_agent_analytics_tables.sql", "r") as f:
    migration_sql = f.read()

print("Executing migration...")
print("=" * 80)

try:
    # Execute the migration SQL
    # Note: Supabase Python client doesn't support direct SQL execution
    # We'll need to use the REST API or execute via Dashboard
    print("Migration SQL ready. Please execute via Supabase Dashboard:")
    print(f"\n1. Go to: {SUPABASE_URL.replace('https://', 'https://supabase.com/dashboard/project/')}")
    print("2. Navigate to: SQL Editor")
    print("3. Copy and paste the migration SQL")
    print("4. Click 'Run'")
    print("\nAlternatively, you can use the Supabase CLI:")
    print("  supabase db execute --file database/migrations/003_create_agent_analytics_tables.sql")
    
    # For now, let's just verify the connection works
    result = supabase.table("agents").select("id").limit(1).execute()
    print(f"\n✓ Successfully connected to Supabase")
    print(f"✓ Migration file is ready at: database/migrations/003_create_agent_analytics_tables.sql")
    
except Exception as e:
    print(f"Error: {e}")
    exit(1)
