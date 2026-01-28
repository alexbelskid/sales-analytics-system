"""
Shared dependencies for the application.
"""

from fastapi import Header, HTTPException, status
from app.config import settings
import secrets

async def verify_admin_access(x_admin_key: str = Header(None, alias="X-Admin-Key")):
    """
    Verify that the request has the correct admin secret key.
    Used for destructive operations like deleting all data.
    """
    # Fail secure: If no admin key is configured, disable admin access entirely
    if not settings.admin_secret_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Admin access is not configured on this server."
        )

    if not x_admin_key:
         raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing admin key header"
        )

    # Constant-time comparison to prevent timing attacks
    if not secrets.compare_digest(x_admin_key, settings.admin_secret_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin key"
        )

    return True
