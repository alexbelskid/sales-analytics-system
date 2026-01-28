from fastapi import Header, HTTPException, status
import secrets
from app.config import settings

async def verify_admin_access(x_admin_key: str = Header(...)):
    """
    Verify that the X-Admin-Key header matches the configured admin secret key.
    Uses constant-time comparison to prevent timing attacks.
    """
    if not settings.admin_secret_key:
        # If no key is configured, deny all access for safety
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Admin access not configured"
        )

    if not secrets.compare_digest(x_admin_key, settings.admin_secret_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin key"
        )
