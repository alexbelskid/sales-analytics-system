from fastapi import Header, HTTPException
from typing import Optional
import secrets
from app.config import settings

async def verify_admin_access(x_admin_key: Optional[str] = Header(None, alias="X-Admin-Key")):
    """
    Dependency to verify admin access using a secret key.
    The key should be provided in the X-Admin-Key header.
    """
    if not settings.admin_secret_key:
        # If admin key is not set in config, we should fail secure or allow local dev?
        # For security, we should probably fail if it's not configured in a real environment.
        # But for this existing codebase, I'll log a warning and block access.
        # Unless it's empty by default, then maybe we should allow?
        # No, allowing empty key is dangerous.
        print("CRITICAL: ADMIN_SECRET_KEY is not set in configuration!")
        raise HTTPException(status_code=500, detail="Server misconfiguration: Admin key not set")

    if not x_admin_key:
        raise HTTPException(status_code=401, detail="Missing admin credentials")

    # Use constant-time comparison to prevent timing attacks
    if not secrets.compare_digest(x_admin_key, settings.admin_secret_key):
        raise HTTPException(status_code=403, detail="Invalid admin credentials")

    return True
