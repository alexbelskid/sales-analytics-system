from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Supabase
    supabase_url: str = ""
    supabase_key: str = ""
    supabase_service_key: str = ""  # Service role key for bypassing RLS
    database_url: str = ""
    
    # AI APIs
    openai_api_key: str = ""
    openai_model: str = "gpt-4-turbo-preview"
    groq_api_key: str = ""
    
    # Gmail / SMTP
    gmail_client_id: str = ""
    gmail_client_secret: str = ""
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 465
    smtp_user: str = ""
    smtp_password: str = ""
    
    # App
    app_name: str = "Alterini AI API"
    debug: bool = True
    frontend_url: str = "http://localhost:3000"
    api_base_url: str = "http://localhost:8000"
    port: int = 8000
    environment: str = "development"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # Ignore any extra env variables


def get_settings() -> Settings:
    return Settings()


settings = get_settings()
