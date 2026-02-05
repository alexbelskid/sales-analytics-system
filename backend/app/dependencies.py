from fastapi import Header, HTTPException, Depends, status
from app.config import get_settings, Settings
import secrets

async def verify_admin_access(
    x_admin_key: str = Header(None, alias="X-Admin-Key"),
    settings: Settings = Depends(get_settings)
):
    """
    Verifies that the request includes the correct admin secret key.
    Used to protect destructive endpoints.
    """
    if not settings.admin_secret_key:
        # Fail securely if the server is not configured
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server administration is not configured. Please set ADMIN_SECRET_KEY."
        )

    if not x_admin_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing admin key"
        )

    # Use constant-time comparison to prevent timing attacks
    if not secrets.compare_digest(x_admin_key, settings.admin_secret_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin key"
        )

    return True
