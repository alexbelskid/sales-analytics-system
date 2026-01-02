from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, Optional
from app.database import supabase
from app.models.email import EmailSettings, EmailSettingsCreate, EmailSettingsUpdate
from app.services.email_connector import EmailConnector

router = APIRouter()

@router.get("/settings", response_model=Optional[EmailSettings])
async def get_email_settings():
    """
    Get current user's email settings.
    """
    if not supabase:
        raise HTTPException(status_code=503, detail="Database not configured")
        
    try:
        # In real app, filter by user_id from auth
        response = supabase.table("email_settings").select("*").limit(1).single().execute()
        if not response.data:
            return None
        return response.data
    except Exception as e:
        # Supabase raises error if no rows found in single()
        return None

@router.post("/settings", response_model=EmailSettings)
async def save_email_settings(settings: EmailSettingsCreate):
    """
    Save or update email settings.
    """
    if not supabase:
        raise HTTPException(status_code=503, detail="Database not configured")

    # Basic logic: UPSERT based on email_address or ID
    # For MVP we assume one setting per user/system
    
    # 1. Check existing
    existing = await get_email_settings()
    
    data = settings.dict(exclude_unset=True)
    # Encrypt password/tokens here in real app
    # data["password_encrypted"] = encrypt(settings.password) 
    # For now saving as plain text (DEMO ONLY)
    if settings.password:
        data["password_encrypted"] = settings.password
    
    if "password" in data:
        del data["password"] # don't save raw or empty password field
    
    try:
        if existing:
            response = supabase.table("email_settings").update(data).eq("id", existing["id"]).execute()
        else:
            response = supabase.table("email_settings").insert(data).execute()
            
        if not response.data or len(response.data) == 0:
            # Fallback for some supabase client versions/configs that might not return data on success
            # or if the operation didn't return a record as expected.
            return await get_email_settings()
            
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.post("/test-connection")
async def test_connection(settings: EmailSettingsCreate):
    """
    Test IMAP/SMTP connection with provided settings.
    Does not save to DB.
    """
    # Prepare settings dict for connector
    conn_settings = settings.dict()
    
    # Auto-detect if needed (though frontend should usually send full details)
    if not settings.imap_server:
        detected = EmailConnector.detect_provider_settings(settings.email_address)
        conn_settings.update(detected)
        
    result = EmailConnector.test_connection(conn_settings)
    
    return {
        "success": result["imap_success"] and result["smtp_success"],
        "details": result,
        "detected_settings": EmailConnector.detect_provider_settings(settings.email_address)
    }

@router.delete("/settings")
async def delete_email_settings():
    """Delete settings (disconnect)"""
    if not supabase:
        raise HTTPException(status_code=503, detail="Database not configured")
        
    try:
        # Get existing ID
        existing = await get_email_settings()
        if existing:
            supabase.table("email_settings").delete().eq("id", existing["id"]).execute()
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
