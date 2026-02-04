from fastapi import Header, HTTPException, status
from app.config import settings
import secrets

async def verify_admin_access(x_admin_key: str = Header(None, alias="X-Admin-Key")):
    """
    Verifies that the request includes the correct admin secret key.
    Used to protect destructive endpoints.
    """
    if not settings.admin_secret_key:
        # Fail secure: if no key is configured, disable admin access entirely
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Admin access is not configured on the server."
        )

    if not x_admin_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-Admin-Key header"
        )

    if not secrets.compare_digest(x_admin_key, settings.admin_secret_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin key"
        )

    return True
