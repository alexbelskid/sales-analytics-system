from fastapi import Header, HTTPException, Depends, status
from app.config import Settings, get_settings
import secrets

async def verify_admin_access(
    x_admin_key: str = Header(None, alias="X-Admin-Key"),
    settings: Settings = Depends(get_settings)
):
    """
    Verifies the admin access key from the header.
    Fails securely (500) if the server is not configured with a secret key.
    """
    if not settings.admin_secret_key:
        # Secure failure: Server is not configured to accept admin commands
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Admin access not configured on server"
        )

    if not x_admin_key or not secrets.compare_digest(x_admin_key, settings.admin_secret_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing admin key"
        )

    return True
