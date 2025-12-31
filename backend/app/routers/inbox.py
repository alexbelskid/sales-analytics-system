from fastapi import APIRouter, HTTPException, Query, Body, BackgroundTasks
from typing import List, Optional
from datetime import datetime
import uuid

from app.database import supabase
from app.models.email import IncomingEmail, EmailResponse, EmailDraftCreate
from app.services.email_connector import EmailConnector
from app.models.email import EmailSettingsCreate # For helper usage

router = APIRouter()

@router.get("/inbox", response_model=List[IncomingEmail])
async def get_inbox_emails(
    filter_status: str = Query("new", description="new, read, archived, sent"),
    category: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    """
    Get emails list with pagination and filtering.
    """
    if not supabase:
        return []
        
    try:
        query = supabase.table("incoming_emails").select("*")
        
        # Apply filters
        if filter_status == "new":
            query = query.neq("status", "archived").neq("status", "sent")
        elif filter_status == "archived":
            query = query.eq("status", "archived")
        elif filter_status == "sent":
            query = query.eq("status", "sent")
            
        if category:
            query = query.eq("category", category)
            
        # Order by newest first
        query = query.order("received_at", desc=True)
        query = query.range(offset, offset + limit - 1)
        
        result = query.execute()
        return result.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{email_id}", response_model=IncomingEmail)
async def get_email_details(email_id: str):
    """Get single email by ID"""
    if not supabase:
        raise HTTPException(status_code=503, detail="Database not configured")
        
    try:
        result = supabase.table("incoming_emails").select("*").eq("id", email_id).single().execute()
        if not result.data:
            raise HTTPException(status_code=404, detail="Email not found")
        return result.data
    except Exception as e:
        raise HTTPException(status_code=404, detail="Email not found")

@router.post("/sync")
async def sync_emails(background_tasks: BackgroundTasks):
    """
    Trigger manual email sync for the current user settings.
    Runs in background to avoid blocking.
    """
    if not supabase:
        raise HTTPException(status_code=503, detail="Database not configured")
        
    try:
        # Get settings
        settings_res = supabase.table("email_settings").select("*").limit(1).single().execute()
        if not settings_res.data:
            raise HTTPException(status_code=400, detail="Email settings not found")
            
        settings = settings_res.data
        
        # Prepare settings dict (decrypt password in real app)
        conn_settings = settings.copy()
        if "password_encrypted" in conn_settings:
            conn_settings["password"] = conn_settings["password_encrypted"]
            
        # Fetch emails
        new_emails = EmailConnector.fetch_emails(conn_settings, limit=20)
        
        # Save to DB (deduplication handled by message_id unique constraint in real app logic)
        # Here we loop and insert safely
        count = 0
        for email in new_emails:
            # Check if exists
            exists = supabase.table("incoming_emails").select("id").eq("message_id", email.get("message_id")).execute()
            if not exists.data:
                # Insert
                new_record = {
                    "settings_id": settings["id"],
                    "sender_email": email["sender"], # Simplified parsing needed here generally
                    "subject": email["subject"],
                    "body_text": email["body_text"],
                    "body_html": email["body_html"],
                    "received_at": datetime.now().isoformat(), # Should parse email date
                    "message_id": email["message_id"],
                    "status": "new"
                }
                supabase.table("incoming_emails").insert(new_record).execute()
                count += 1
                
        # Update last sync time
        supabase.table("email_settings").update({"last_sync_at": datetime.now().isoformat()}).eq("id", settings["id"]).execute()
        
        return {"status": "success", "new_emails_count": count}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{email_id}/send")
async def send_reply(email_id: str, draft: EmailDraftCreate):
    """
    Send a reply to an email.
    """
    if not supabase:
        raise HTTPException(status_code=503, detail="Database not configured")
        
    try:
        # Get original email to reply to
        orig_res = supabase.table("incoming_emails").select("*").eq("id", email_id).single().execute()
        if not orig_res.data:
            raise HTTPException(status_code=404, detail="Email not found")
        orig_email = orig_res.data
        
        # Get settings
        settings_res = supabase.table("email_settings").select("*").limit(1).single().execute()
        if not settings_res.data:
            raise HTTPException(status_code=400, detail="Settings not found")
        settings = settings_res.data
        
        # Prepare sending settings
        conn_settings = settings.copy()
        if "password_encrypted" in conn_settings:
            conn_settings["password"] = conn_settings["password_encrypted"]
            
        # Send
        subject = f"Re: {orig_email.get('subject', '')}"
        result = EmailConnector.send_email(
            conn_settings, 
            to_email=orig_email["sender_email"], # Assume straight email string for now
            subject=subject, 
            body_html=draft.draft_text, # Using draft text as HTML body
            in_reply_to=orig_email.get("message_id")
        )
        
        if result["success"]:
            # Save response
            resp_record = {
                "email_id": email_id,
                "final_text": draft.draft_text,
                "status": "sent",
                "sent_at": datetime.now().isoformat(),
                "tone_id": str(draft.tone_id) if draft.tone_id else None
            }
            supabase.table("email_responses").insert(resp_record).execute()
            
            # Update original email status
            supabase.table("incoming_emails").update({"status": "replied"}).eq("id", email_id).execute()
            
            return {"success": True}
        else:
            raise HTTPException(status_code=500, detail=f"Failed to send: {result.get('error')}")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
