from fastapi import Header, HTTPException, Depends
from app.config import Settings, get_settings
import secrets

async def verify_admin_access(
    x_admin_key: str = Header(..., alias="X-Admin-Key", description="Admin secret key for destructive operations"),
    settings: Settings = Depends(get_settings)
):
    """
    Verify that the request has a valid admin key.
    Use for destructive operations.
    """
    if not settings.admin_secret_key:
        # Fail secure: If no admin key is configured, deny all admin access
        raise HTTPException(
            status_code=500,
            detail="Server configuration error: Admin key not set"
        )

    # Use constant-time comparison to prevent timing attacks
    if not secrets.compare_digest(x_admin_key, settings.admin_secret_key):
        raise HTTPException(
            status_code=403,
            detail="Invalid admin key"
        )

    return True
