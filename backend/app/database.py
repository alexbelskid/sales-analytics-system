from supabase import create_client, Client
from typing import Optional
from app.config import settings

# Initialize Supabase client (None if not configured)
supabase: Optional[Client] = None

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


def get_supabase() -> Optional[Client]:
    """Dependency for getting Supabase client"""
    return supabase
