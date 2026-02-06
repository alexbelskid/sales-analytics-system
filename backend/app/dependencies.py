from fastapi import HTTPException, Security, Depends
from fastapi.security.api_key import APIKeyHeader
from app.config import settings
import secrets

# Define API Key Header scheme
api_key_header = APIKeyHeader(name="X-Admin-Key", auto_error=False)

async def verify_admin_access(api_key: str = Security(api_key_header)):
    """
    Verify that the request has the correct X-Admin-Key header.
    This protects destructive administrative endpoints.
    """
    # 1. Fail secure: If no admin key is configured on the server, deny all access
    if not settings.admin_secret_key:
        raise HTTPException(
            status_code=500,
            detail="Admin secret key not configured. Cannot perform administrative action."
        )

    # 2. Check key
    if not api_key or not secrets.compare_digest(api_key, settings.admin_secret_key):
        raise HTTPException(
            status_code=403,
            detail="Invalid or missing Admin Key"
        )

    return True
