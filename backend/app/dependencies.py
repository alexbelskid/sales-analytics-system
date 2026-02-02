from fastapi import Header, HTTPException, status
from app.config import settings
import secrets
import logging

logger = logging.getLogger(__name__)

async def verify_admin_access(x_admin_key: str = Header(None, alias="X-Admin-Key")):
    """
    Dependency to verify admin access via X-Admin-Key header.
    """
    if not settings.admin_secret_key:
        logger.error("Admin secret key is not configured!")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server configuration error: Admin key not set"
        )

    if not x_admin_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing admin key"
        )

    # Secure constant-time comparison
    if not secrets.compare_digest(x_admin_key, settings.admin_secret_key):
        logger.warning(f"Invalid admin key attempt: {x_admin_key[:3]}...")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin key"
        )

    return True
