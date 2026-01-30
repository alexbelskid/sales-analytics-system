from fastapi import Header, HTTPException
from app.config import settings
import secrets

async def verify_admin_access(x_admin_key: str = Header(..., description="Admin Secret Key")):
    """
    Verifies the X-Admin-Key header against the configured ADMIN_SECRET_KEY.
    """
    if not settings.admin_secret_key:
        # Fail secure: if admin key is not configured, deny all access to admin endpoints
        raise HTTPException(
            status_code=500,
            detail="Server misconfiguration: Admin key not set"
        )

    # Use constant-time comparison to prevent timing attacks
    if not secrets.compare_digest(x_admin_key, settings.admin_secret_key):
        raise HTTPException(status_code=401, detail="Invalid Admin Key")

    return True
