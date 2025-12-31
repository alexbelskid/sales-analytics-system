from typing import Dict, Any, List, Optional
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import base64
from email.mime.text import MIMEText
from datetime import datetime

class GmailAPIConnector:
    """
    Connector for Gmail API (OAuth2).
    """

    @staticmethod
    def _get_service(settings: Dict[str, Any]):
        creds = Credentials(
            token=settings.get("oauth_token_encrypted"),
            refresh_token=settings.get("oauth_refresh_token"),
            token_uri="https://oauth2.googleapis.com/token",
            client_id=settings.get("client_id"), # In real app, get from config
            client_secret=settings.get("client_secret")
        )
        return build('gmail', 'v1', credentials=creds)

    @staticmethod
    def fetch_emails(settings: Dict[str, Any], limit: int = 20) -> List[Dict[str, Any]]:
        """Fetch emails via Gmail API"""
        try:
            service = GmailAPIConnector._get_service(settings)
            results = service.users().messages().list(userId='me', maxResults=limit).execute()
            messages = results.get('messages', [])
            
            emails_found = []
            for msg_info in messages:
                msg = service.users().messages().get(userId='me', id=msg_info['id']).execute()
                payload = msg.get('payload', {})
                headers = payload.get('headers', [])
                
                subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), '(No Subject)')
                sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), 'Unknown')
                date = next((h['value'] for h in headers if h['name'].lower() == 'date'), '')
                
                # Get body
                body_text = ""
                if 'parts' in payload:
                    for part in payload['parts']:
                        if part['mimeType'] == 'text/plain':
                            data = part['body'].get('data')
                            if data:
                                body_text = base64.urlsafe_b64decode(data).decode('utf-8')
                else:
                    data = payload.get('body', {}).get('data')
                    if data:
                        body_text = base64.urlsafe_b64decode(data).decode('utf-8')

                emails_found.append({
                    "message_id": msg.get('id'),
                    "sender": sender,
                    "subject": subject,
                    "received_at": date,
                    "body_text": body_text,
                    "body_html": body_text # Simplified for MVP
                })
            
            return emails_found
        except Exception as e:
            print(f"Gmail API Fetch Error: {str(e)}")
            return []

    @staticmethod
    def send_email(settings: Dict[str, Any], to_email: str, subject: str, body_html: str) -> bool:
        """Send email via Gmail API"""
        try:
            service = GmailAPIConnector._get_service(settings)
            
            message = MIMEText(body_html, 'html')
            message['to'] = to_email
            message['from'] = settings.get("email_address")
            message['subject'] = subject
            
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            
            service.users().messages().send(userId='me', body={'raw': raw_message}).execute()
            return True
        except Exception as e:
            print(f"Gmail API Send Error: {str(e)}")
            return False
