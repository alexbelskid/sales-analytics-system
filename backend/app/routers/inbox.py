from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, Dict, List
from app.database import supabase
from app.config import settings
import imaplib
import email
from email.header import decode_header
import datetime
import socket
import time
from pydantic import BaseModel

router = APIRouter()

class EmailConfig(BaseModel):
    email: str
    app_password: str

@router.post("/sync")
async def sync_emails(config: Optional[EmailConfig] = None):
    """Sync emails using IMAP with timeout protection"""
    start_time = time.time()
    
    # Set socket timeout to prevent hanging
    socket.setdefaulttimeout(10)
    
    try:
        # 1. Get credentials
        email_addr = ""
        app_password = ""
        user_settings = None
        
        if config:
            email_addr = config.email
            app_password = config.app_password
        else:
            # Check DB
            if not supabase:
                 return {"status": "error", "message": "Database not connected", "new_emails_count": 0}
                 
            settings_response = supabase.table("email_settings").select("*").execute()
            if not settings_response.data:
                return {"status": "error", "message": "Settings not found", "new_emails_count": 0}
            
            user_settings = settings_response.data[0]
            email_addr = user_settings.get("email")
            # Try to get password from potential fields
            app_password = user_settings.get("app_password") or user_settings.get("password_encrypted") or user_settings.get("imap_password")
            
            if not email_addr or not app_password:
                 return {"status": "error", "message": "Credentials missing in DB", "new_emails_count": 0}

        # 2. Connect to IMAP
        # Default to Yandex as requested or try to infer, but for now hardcode or use settings if available
        imap_server = "imap.yandex.ru" # Fallback
        imap_port = 993
        
        # If we have settings from DB, try to use them
        if not config and user_settings:
            imap_server = user_settings.get("imap_server") or "imap.yandex.ru"
            imap_port = int(user_settings.get("imap_port") or 993)

        mail = imaplib.IMAP4_SSL(imap_server, imap_port)
        mail.login(email_addr, app_password)
        mail.select("inbox")
        
        # 3. Fetch emails
        status, messages = mail.search(None, "UNSEEN")
        email_ids = messages[0].split()
        
        new_emails_count = 0
        
        for email_id in email_ids[-5:]:  # Last 5 unseen (optimized for speed)
            try:
                status, msg_data = mail.fetch(email_id, "(RFC822)")
                msg = email.message_from_bytes(msg_data[0][1])
                
                # Decode subject
                subject_header = decode_header(msg["Subject"])[0]
                subject = subject_header[0]
                if isinstance(subject, bytes):
                    subject = subject.decode(errors="ignore")
                
                # Decode From
                from_header = msg.get("From", "")
                
                # Get Body
                body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            body = part.get_payload(decode=True).decode(errors="ignore")
                            break
                else:
                    body = msg.get_payload(decode=True).decode(errors="ignore")
                
                # Save to DB
                if supabase:
                    # Check if exists (simplified)
                    email_data = {
                        "subject": subject,
                        "body_text": body[:1000] if body else "", # Limit for safety
                        "sender_email": from_header, # Simplification
                        "received_at": datetime.datetime.now().isoformat(),
                        "is_read": False,
                        "folder": "inbox", # Required by schema usually
                        "settings_id": user_settings["id"] if user_settings else None
                    }
                    try:
                        supabase.table("incoming_emails").insert(email_data).execute()
                        new_emails_count += 1
                    except Exception as insert_err:
                        print(f"Insert error: {insert_err}")
                        pass # Ignore duplicates or schema mismatch for now
                        
            except Exception as e:
                print(f"Error processing email {email_id}: {e}")
                continue
                
        mail.close()
        mail.logout()
        
        elapsed_time = time.time() - start_time
        print(f"✅ Email sync completed in {elapsed_time:.2f}s - {new_emails_count} new emails")
        
        return {
            "status": "success", 
            "new_emails_count": new_emails_count,
            "sync_time": round(elapsed_time, 2)
        }
        
    except socket.timeout:
        elapsed_time = time.time() - start_time
        print(f"⏱️ IMAP timeout after {elapsed_time:.2f}s")
        return {
            "status": "timeout", 
            "message": "Email sync timed out. Please try again.", 
            "new_emails_count": 0
        }
    except Exception as e:
        elapsed_time = time.time() - start_time
        print(f"❌ Sync error after {elapsed_time:.2f}s: {e}")
        return {
            "status": "error", 
            "message": str(e), 
            "new_emails_count": 0
        }
    finally:
        # Reset socket timeout to default
        socket.setdefaulttimeout(None)

@router.get("/inbox")
async def get_inbox(filter_status: str = "new", limit: int = 50):
    if not supabase:
        return []
    
    try:
        query = supabase.table("incoming_emails").select("*").order("received_at", desc=True).limit(limit)
        # Filters can be added here
        res = query.execute()
        return res.data
    except Exception:
        return []

@router.post("/generate-response")
async def generate_response(request: Dict):
    """Simple generation without AI dependency for now"""
    subject = request.get("email", {}).get("subject", "")
    tone = "professional" # Default
    
    response = f'''Здравствуйте!

Спасибо за ваше письмо по теме "{subject}".

Мы получили ваш запрос и обработаем его в ближайшее время.

[Сгенерировано Sales AI]

С уважением,
Команда Sales AI'''
    
    return {
        "original_subject": subject,
        "generated_reply": response,
        "status": "success",
        "tone_used": tone
    }
