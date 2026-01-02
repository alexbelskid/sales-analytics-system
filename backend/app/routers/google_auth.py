from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse
from google_auth_oauthlib.flow import Flow
from app.config import settings
from app.database import supabase
import json
import os

router = APIRouter()

# Scopes required for the application
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/userinfo.email',
    'openid'
]

def get_google_config():
    return {
        "web": {
            "client_id": settings.gmail_client_id,
            "client_secret": settings.gmail_client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [f"{settings.api_base_url}/api/google/callback"]
        }
    }

@router.get("/auth-url")
async def get_auth_url():
    """Generate Google OAuth URL"""
    if not settings.gmail_client_id or not settings.gmail_client_secret:
        raise HTTPException(status_code=400, detail="Google API credentials not configured")
    
    flow = Flow.from_client_config(
        get_google_config(),
        scopes=SCOPES,
        redirect_uri=f"{settings.api_base_url}/api/google/callback"
    )
    
    auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline')
    return {"url": auth_url}

@router.get("/callback")
async def callback(request: Request):
    """Handle Google OAuth callback"""
    code = request.query_params.get("code")
    if not code:
        raise HTTPException(status_code=400, detail="Missing authorization code")
    
    flow = Flow.from_client_config(
        get_google_config(),
        scopes=SCOPES,
        redirect_uri=f"{settings.api_base_url}/api/google/callback"
    )
    
    try:
        flow.fetch_token(code=code)
        credentials = flow.credentials
        
        # In a real app, we'd get the user email from the token
        # For MVP, we save it as a setting
        token_data = {
            "token": credentials.token,
            "refresh_token": credentials.refresh_token,
            "token_uri": credentials.token_uri,
            "client_id": credentials.client_id,
            "client_secret": credentials.client_secret,
            "scopes": credentials.scopes
        }
        
        # Save to Supabase (Simplified logic)
        # 1. Get user info (optional)
        # 2. Update email_settings table
        
        # For now, we redirect to frontend with success/fail
        # In production, this would be more robust
        frontend_url = f"{settings.frontend_url}/settings/email?oauth_success=true"
        # We also need to save these credentials to the DB.
        # Since we don't have the user_id context here easily without Auth, 
        # let's assume we update the only existing setting for now.
        
        save_data = {
            "connection_type": "gmail_api",
            "email_provider": "gmail",
            "oauth_token_encrypted": credentials.token,
            "oauth_refresh_token": credentials.refresh_token,
            "connection_status": "connected"
        }
        
        existing = supabase.table("email_settings").select("id").limit(1).execute()
        if existing.data:
            supabase.table("email_settings").update(save_data).eq("id", existing.data[0]["id"]).execute()
        else:
            # We need an email address. Let's try to get it from Google API
            from googleapiclient.discovery import build
            service = build('oauth2', 'v2', credentials=credentials)
            user_info = service.userinfo().get().execute()
            save_data["email_address"] = user_info.get("email")
            supabase.table("email_settings").insert(save_data).execute()

        return RedirectResponse(url=frontend_url)
    except Exception as e:
        return RedirectResponse(url=f"{settings.frontend_url}/settings/email?oauth_error={str(e)}")
