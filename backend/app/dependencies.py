from fastapi import Header, HTTPException, Depends
from typing import Optional
import secrets
from app.config import settings

async def verify_admin_access(x_admin_key: Optional[str] = Header(None, alias="X-Admin-Key")):
    """
    Verify that the request has the correct admin key for critical operations.
    If no key is configured in settings:
      - In Production: BLOCK access (fail safe)
      - In Development: ALLOW access (dev convenience)
    """
    # 1. If key is configured, it MUST be provided and match
    if settings.admin_secret_key:
        # Use secrets.compare_digest to prevent timing attacks
        if not x_admin_key or not secrets.compare_digest(x_admin_key, settings.admin_secret_key):
             raise HTTPException(status_code=403, detail="Invalid or missing admin key")
        return True

    # 2. If no key configured, check environment
    # Using lower() to be safe against "Production" vs "production"
    env = (settings.environment or "development").lower()
    if env == "production":
         # In prod, if no key is set, we block destructive actions by default
         raise HTTPException(status_code=403, detail="Admin key not configured in production")

    # 3. Allow in development if no key configured
    return True
