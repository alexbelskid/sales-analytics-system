from fastapi import Header, HTTPException
import secrets
from app.config import settings

async def verify_admin_access(x_admin_key: str = Header(None)):
    """
    Verifies that the request contains the correct admin secret key.
    Used for protecting destructive or sensitive endpoints.
    """
    if not x_admin_key:
        raise HTTPException(status_code=403, detail="Admin key required")

    # Use constant-time comparison to prevent timing attacks
    if not secrets.compare_digest(x_admin_key, settings.admin_secret_key):
        raise HTTPException(status_code=403, detail="Invalid admin key")

    return True
