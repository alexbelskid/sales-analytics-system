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
import asyncio
from pydantic import BaseModel

router = APIRouter()

class EmailConfig(BaseModel):
    email: str
    app_password: str

def _sync_emails_blocking(config: Optional[EmailConfig] = None):
    """Blocking function to handle IMAP sync"""
    start_time = time.time()
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

        # Use timeout in constructor instead of socket.setdefaulttimeout
        mail = imaplib.IMAP4_SSL(imap_server, imap_port, timeout=10)
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


@router.post("/sync")
async def sync_emails(config: Optional[EmailConfig] = None):
    """Sync emails using IMAP with timeout protection"""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _sync_emails_blocking, config)

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
    """
    Manual email response generation.
    Accepts: {
        "from": "sender@example.com",
        "subject": "Email Subject",
        "body": "Email Body text...",
        "tone": "professional" | "friendly" | "formal" ...
    }
    """
    from app.services.ai_service import generate_manual_response
    
    sender = request.get("from", "")
    subject = request.get("subject", "")
    body = request.get("body", "")
    tone = request.get("tone", "professional")
    
    response = await generate_manual_response(subject, body, sender, tone)
    
    return {
        "original_subject": subject,
        "generated_reply": response,
        "status": "success",
        "tone_used": tone
    }


@router.post("/test-imap-only")
async def test_imap_only(config: EmailConfig):
    """Test IMAP connection only - for debugging"""
    start_time = time.time()
    socket.setdefaulttimeout(10)
    
    steps = []
    try:
        steps.append("1. Starting IMAP test...")
        steps.append(f"2. Email: {config.email}")
        steps.append("3. Connecting to imap.gmail.com:993...")
        
        mail = imaplib.IMAP4_SSL("imap.gmail.com", 993)
        elapsed = time.time() - start_time
        steps.append(f"4. Connected in {elapsed:.2f}s")
        
        steps.append("5. Logging in...")
        mail.login(config.email, config.app_password)
        elapsed = time.time() - start_time
        steps.append(f"6. Login successful in {elapsed:.2f}s")
        
        steps.append("7. Selecting INBOX...")
        status, messages = mail.select("INBOX")
        msg_count = int(messages[0])
        steps.append(f"8. INBOX has {msg_count} messages")
        
        mail.close()
        mail.logout()
        elapsed = time.time() - start_time
        steps.append(f"9. Test completed in {elapsed:.2f}s")
        
        return {
            "success": True,
            "message": f"IMAP OK! {msg_count} messages in inbox",
            "time_seconds": round(elapsed, 2),
            "steps": steps
        }
        
    except socket.timeout:
        elapsed = time.time() - start_time
        steps.append(f"ERROR: Timeout after {elapsed:.2f}s")
        return {
            "success": False,
            "error": "Connection timeout (10s)",
            "time_seconds": round(elapsed, 2),
            "steps": steps
        }
    except imaplib.IMAP4.error as e:
        elapsed = time.time() - start_time
        steps.append(f"ERROR: IMAP error - {str(e)}")
        return {
            "success": False,
            "error": f"IMAP Error: {str(e)}",
            "time_seconds": round(elapsed, 2),
            "steps": steps
        }
    except Exception as e:
        elapsed = time.time() - start_time
        steps.append(f"ERROR: {type(e).__name__} - {str(e)}")
        return {
            "success": False,
            "error": f"{type(e).__name__}: {str(e)}",
            "time_seconds": round(elapsed, 2),
            "steps": steps
        }
    finally:
        socket.setdefaulttimeout(None)


@router.post("/test-smtp-only")
async def test_smtp_only(config: EmailConfig):
    """Test SMTP connection only - trying PORT 587 (STARTTLS)"""
    import smtplib
    import ssl
    
    start_time = time.time()
    socket.setdefaulttimeout(15)
    
    steps = []
    try:
        steps.append("1. Starting SMTP test (PORT 587)...")
        steps.append(f"2. Email: {config.email}")
        steps.append("3. Connecting to smtp.gmail.com:587 (TLS)...")
        
        # Try connect without SSL first
        server = smtplib.SMTP("smtp.gmail.com", 587)
        elapsed = time.time() - start_time
        steps.append(f"4. Connected in {elapsed:.2f}s")
        
        steps.append("5. Starting TLS...")
        context = ssl.create_default_context()
        server.starttls(context=context)
        
        steps.append("6. Logging in...")
        server.login(config.email, config.app_password)
        elapsed = time.time() - start_time
        steps.append(f"7. Login successful in {elapsed:.2f}s")
        
        server.quit()
        
        return {
            "success": True,
            "message": "SMTP OK (Port 587)! Ready to send emails",
            "time_seconds": round(elapsed, 2),
            "steps": steps
        }
        
    except socket.timeout:
        elapsed = time.time() - start_time
        steps.append(f"ERROR: Timeout after {elapsed:.2f}s")
        return {
            "success": False,
            "error": "Connection timeout (15s)",
            "time_seconds": round(elapsed, 2),
            "steps": steps
        }
    except Exception as e:
        elapsed = time.time() - start_time
        steps.append(f"ERROR: {type(e).__name__} - {str(e)}")
        return {
            "success": False,
            "error": f"{type(e).__name__}: {str(e)}",
            "time_seconds": round(elapsed, 2),
            "steps": steps
        }
    finally:
        socket.setdefaulttimeout(None)
