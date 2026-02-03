from fastapi import Header, HTTPException, Depends
from app.config import settings
import secrets

async def verify_admin_access(x_admin_key: str = Header(None, alias="X-Admin-Key")):
    """
    Verify that the request has the correct admin key.
    Used for securing destructive or sensitive endpoints.
    """
    if not settings.admin_secret_key:
        # Fail securely if no key is configured
        raise HTTPException(
            status_code=500,
            detail="Admin access not configured on server"
        )

    if not x_admin_key:
        raise HTTPException(
            status_code=401,
            detail="Admin key required"
        )

    if not secrets.compare_digest(x_admin_key, settings.admin_secret_key):
        raise HTTPException(
            status_code=403,
            detail="Invalid admin key"
        )

    return True
