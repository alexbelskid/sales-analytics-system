import imaplib
import smtplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import decode_header
import ssl
from typing import Dict, Any, Optional, List
from datetime import datetime
import re

class EmailConnector:
    """
    Universal Email Connector for IMAP/SMTP.
    Handles connection testing, fetching emails, and sending replies.
    """

    PROVIDER_SETTINGS = {
        "gmail": {
            "imap_server": "imap.gmail.com",
            "imap_port": 993,
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587
        },
        "outlook": {
            "imap_server": "outlook.office365.com",
            "imap_port": 993,
            "smtp_server": "smtp.office365.com",
            "smtp_port": 587
        },
        "yandex": {
            "imap_server": "imap.yandex.com",
            "imap_port": 993,
            "smtp_server": "smtp.yandex.com",
            "smtp_port": 465 # Yandex prefers SSL on 465
        },
        "mail_ru": {
            "imap_server": "imap.mail.ru",
            "imap_port": 993,
            "smtp_server": "smtp.mail.ru",
            "smtp_port": 465
        },
        "rambler": {
            "imap_server": "imap.rambler.ru",
            "imap_port": 993,
            "smtp_server": "smtp.rambler.ru",
            "smtp_port": 465
        },
        "yahoo": {
            "imap_server": "imap.mail.yahoo.com",
            "imap_port": 993,
            "smtp_server": "smtp.mail.yahoo.com",
            "smtp_port": 587
        }
    }

    @classmethod
    def detect_provider_settings(cls, email_address: str) -> Optional[Dict[str, Any]]:
        """
        Auto-detect IMAP/SMTP settings based on email domain.
        """
        domain = email_address.split("@")[-1].lower()
        
        # Check known providers
        if "gmail.com" in domain:
            return cls.PROVIDER_SETTINGS["gmail"]
        elif "outlook.com" in domain or "hotmail.com" in domain or "live.com" in domain:
            return cls.PROVIDER_SETTINGS["outlook"]
        elif "yandex" in domain:
            return cls.PROVIDER_SETTINGS["yandex"]
        elif "mail.ru" in domain or "list.ru" in domain or "bk.ru" in domain or "inbox.ru" in domain:
            return cls.PROVIDER_SETTINGS["mail_ru"]
        elif "rambler.ru" in domain:
            return cls.PROVIDER_SETTINGS["rambler"]
        elif "yahoo.com" in domain:
            return cls.PROVIDER_SETTINGS["yahoo"]
            
        # Try generic corporate settings (heuristic)
        return {
            "imap_server": f"imap.{domain}",
            "imap_port": 993,
            "smtp_server": f"smtp.{domain}",
            "smtp_port": 465  # Changed from 587 for Railway compatibility
        }

    @staticmethod
    def test_connection(settings: Dict[str, Any]) -> Dict[str, Any]:
        """
        Test incoming (IMAP) and outgoing (SMTP) connections.
        """
        result = {
            "imap_success": False,
            "smtp_success": False,
            "error": None
        }

        email_user = settings.get("email_address")
        password = settings.get("password")
        
        # Test IMAP
        try:
            imap_server = settings.get("imap_server")
            imap_port = int(settings.get("imap_port", 993))
            
            mail = imaplib.IMAP4_SSL(imap_server, imap_port)
            mail.login(email_user, password)
            mail.logout()
            result["imap_success"] = True
        except Exception as e:
            result["error"] = f"IMAP Error: {str(e)}"
            return result

        # Test SMTP
        try:
            smtp_server = settings.get("smtp_server")
            smtp_port = int(settings.get("smtp_port", 587))
            
            context = ssl.create_default_context()
            
            if smtp_port == 465:
                # SSL connection
                with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as server:
                    server.login(email_user, password)
            else:
                # TLS connection
                with smtplib.SMTP(smtp_server, smtp_port) as server:
                    server.starttls(context=context)
                    server.login(email_user, password)
            
            result["smtp_success"] = True
        except Exception as e:
            result["error"] = f"SMTP Error: {str(e)}"
            return result
            
        return result

    @staticmethod
    def send_email(settings: Dict[str, Any], to_email: str, subject: str, body_html: str, in_reply_to: str = None) -> Dict[str, Any]:
        """
        Send an email via SMTP.
        """
        email_user = settings.get("email_address")
        password = settings.get("password")
        smtp_server = settings.get("smtp_server")
        smtp_port = int(settings.get("smtp_port", 587))

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = email_user
        msg["To"] = to_email
        msg["Date"] = email.utils.formatdate(localtime=True)
        
        if in_reply_to:
            msg["In-Reply-To"] = in_reply_to
            msg["References"] = in_reply_to

        # Attach textual parts
        # For this version we mainly support HTML, but could strip tags for plain text
        part_html = MIMEText(body_html, "html")
        msg.attach(part_html)

        try:
            context = ssl.create_default_context()
            if smtp_port == 465:
                with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as server:
                    server.login(email_user, password)
                    server.sendmail(email_user, to_email, msg.as_string())
            else:
                with smtplib.SMTP(smtp_server, smtp_port) as server:
                    server.starttls(context=context)
                    server.login(email_user, password)
                    server.sendmail(email_user, to_email, msg.as_string())
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def fetch_emails(settings: Dict[str, Any], limit: int = 20) -> List[Dict[str, Any]]:
        """
        Fetch recent emails via IMAP.
        Simplified version: just gets the latest 'limit' emails from INBOX.
        """
        email_user = settings.get("email_address")
        password = settings.get("password")
        imap_server = settings.get("imap_server")
        imap_port = int(settings.get("imap_port", 993))
        
        emails_found = []

        try:
            mail = imaplib.IMAP4_SSL(imap_server, imap_port)
            mail.login(email_user, password)
            mail.select("INBOX")

            # Search for all emails
            # In a real sync scenario, we'd search by date or UID
            _, messages = mail.search(None, "ALL")
            email_ids = messages[0].split()
            
            # Get latest 'limit' emails (reverse order)
            latest_email_ids = email_ids[-limit:]
            latest_email_ids.reverse()

            for e_id in latest_email_ids:
                _, msg_data = mail.fetch(e_id, "(RFC822)")
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        try:
                            msg = email.message_from_bytes(response_part[1])
                            
                            # Decode subject
                            subject, encoding = decode_header(msg["Subject"])[0]
                            if isinstance(subject, bytes):
                                subject = subject.decode(encoding if encoding else "utf-8", errors="replace")
                            
                            # Decode sender
                            from_ = msg.get("From")
                            
                            # Extract body
                            body_text = ""
                            body_html = ""
                            
                            if msg.is_multipart():
                                for part in msg.walk():
                                    content_type = part.get_content_type()
                                    content_disposition = str(part.get("Content-Disposition"))
                                    
                                    if "attachment" not in content_disposition:
                                        payload = part.get_payload(decode=True)
                                        if payload:
                                            charset = part.get_content_charset() or "utf-8"
                                            text = payload.decode(charset, errors="replace")
                                            if content_type == "text/plain":
                                                body_text += text
                                            elif content_type == "text/html":
                                                body_html += text
                            else:
                                payload = msg.get_payload(decode=True)
                                if payload:
                                    charset = msg.get_content_charset() or "utf-8"
                                    text = payload.decode(charset, errors="replace")
                                    if msg.get_content_type() == "text/html":
                                        body_html = text
                                    else:
                                        body_text = text

                            emails_found.append({
                                "message_id": msg.get("Message-ID"),
                                "sender": from_,
                                "subject": subject,
                                "received_at": msg.get("Date"), # Parse this properly in real app
                                "body_text": body_text,
                                "body_html": body_html
                            })
                        except Exception as parse_err:
                            print(f"Error parsing email {e_id}: {parse_err}")
                            continue

            mail.logout()
            return emails_found

        except Exception as e:
            print(f"IMAP Fetch Error: {str(e)}")
            raise e

