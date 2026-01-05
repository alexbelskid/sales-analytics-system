from supabase import create_client, Client
from typing import Optional
from app.config import settings

# Initialize Supabase client (None if not configured)
supabase: Optional[Client] = None
supabase_admin: Optional[Client] = None  # Admin client with service_role (bypasses RLS)

# Only create client if URL and KEY are provided
if settings.supabase_url and settings.supabase_key:
    try:
        supabase = create_client(
            settings.supabase_url,
            settings.supabase_key
        )
    except Exception as e:
        print(f"Warning: Could not connect to Supabase: {e}")
        supabase = None
else:
    print("Warning: SUPABASE_URL and SUPABASE_KEY not configured. Database features disabled.")

# Create admin client if service key is provided
if settings.supabase_url and settings.supabase_service_key:
    try:
        supabase_admin = create_client(
            settings.supabase_url,
            settings.supabase_service_key
        )
        print("Supabase admin client initialized (RLS bypass enabled)")
    except Exception as e:
        print(f"Warning: Could not create Supabase admin client: {e}")
        supabase_admin = None


def get_supabase() -> Optional[Client]:
    """Dependency for getting Supabase client"""
    return supabase

def get_supabase_admin() -> Optional[Client]:
    """Get admin client that bypasses RLS (for imports)"""
    return supabase_admin or supabase  # Fallback to regular client
