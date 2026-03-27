from fastapi import Header, HTTPException, Depends
from app.config import Settings, get_settings
import secrets

async def verify_admin_access(
    x_admin_key: str = Header(..., description="Admin Secret Key"),
    settings: Settings = Depends(get_settings)
) -> bool:
    """
    Verify admin access using X-Admin-Key header.
    Protected against timing attacks.
    """
    if not settings.admin_secret_key:
        # Fail securely if no key is configured
        raise HTTPException(
            status_code=500,
            detail="Admin secret key not configured"
        )

    if not secrets.compare_digest(x_admin_key, settings.admin_secret_key):
        raise HTTPException(
            status_code=401,
            detail="Invalid admin key"
        )

    return True
