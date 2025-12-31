from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

# --- Email Settings Models ---

class EmailSettingsBase(BaseModel):
    email_address: EmailStr
    email_provider: str = Field(..., description="gmail, outlook, yandex, mail_ru, etc.")
    connection_type: str = Field("imap", description="imap, gmail_api, graph_api")
    
    imap_server: Optional[str] = None
    imap_port: int = 993
    smtp_server: Optional[str] = None
    smtp_port: int = 587
    use_ssl: bool = True
    
    auto_sync_enabled: bool = True
    sync_interval_minutes: int = 10

class EmailSettingsCreate(EmailSettingsBase):
    password: Optional[str] = None # Plain text, to be encrypted
    oauth_token: Optional[str] = None
    oauth_refresh_token: Optional[str] = None

class EmailSettingsUpdate(BaseModel):
    email_address: Optional[EmailStr] = None
    email_provider: Optional[str] = None
    connection_type: Optional[str] = None
    imap_server: Optional[str] = None
    imap_port: Optional[int] = None
    smtp_server: Optional[str] = None
    smtp_port: Optional[int] = None
    password: Optional[str] = None
    auto_sync_enabled: Optional[bool] = None
    sync_interval_minutes: Optional[int] = None
    is_active: Optional[bool] = None

class EmailSettings(EmailSettingsBase):
    id: UUID
    user_id: Optional[UUID] = None
    # Don't return secrets in default model
    connection_status: str
    last_sync_at: Optional[datetime] = None
    last_sync_error: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# --- Incoming Email Models ---

class IncomingEmailBase(BaseModel):
    sender_email: EmailStr
    sender_name: Optional[str] = None
    recipient_email: Optional[str] = None
    subject: Optional[str] = None
    body_text: Optional[str] = None
    body_html: Optional[str] = None
    received_at: datetime
    message_id: Optional[str] = None
    category: str = "other"
    priority: str = "normal"
    is_read: bool = False

class IncomingEmail(IncomingEmailBase):
    id: UUID
    settings_id: UUID
    status: str
    in_reply_to: Optional[str] = None
    thread_id: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

# --- Email Response/Draft Models ---

class EmailDraftCreate(BaseModel):
    email_id: UUID
    draft_text: str
    tone_id: Optional[UUID] = None

class EmailResponseBase(BaseModel):
    draft_text: Optional[str] = None
    final_text: Optional[str] = None
    tone_name: Optional[str] = None
    status: str

class EmailResponse(EmailResponseBase):
    id: UUID
    email_id: UUID
    sent_at: Optional[datetime] = None
    send_error: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# --- Tone Settings Models ---

class ToneSettingBase(BaseModel):
    tone_name: str
    display_name: Optional[str] = None
    description: Optional[str] = None
    is_default: bool = False
    
    formality_level: int = Field(5, ge=1, le=10)
    friendliness_level: int = Field(5, ge=1, le=10)
    detail_level: int = Field(5, ge=1, le=10)
    
    use_emojis: bool = False
    greeting_style: str = "formal"
    greeting_text: Optional[str] = None
    closing_style: str = "formal"
    closing_text: Optional[str] = None
    
    language: str = "ru"
    use_you_formal: bool = True
    signature_text: Optional[str] = None
    custom_instructions: Optional[str] = None

class ToneSettingCreate(ToneSettingBase):
    pass

class ToneSetting(ToneSettingBase):
    id: UUID
    user_id: Optional[UUID] = None
    is_system: bool = False
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# --- Template Models ---

class TemplateBase(BaseModel):
    name: str
    description: Optional[str] = None
    category: str = "general"
    template_text: str
    placeholders: Dict[str, str] = {}
    tone_id: Optional[UUID] = None
    language: str = "ru"

class TemplateCreate(TemplateBase):
    pass

class Template(TemplateBase):
    id: UUID
    user_id: Optional[UUID] = None
    usage_count: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
