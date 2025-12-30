from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.database import supabase
from app.services.ai_service import generate_email_reply

router = APIRouter()


class EmailContent(BaseModel):
    subject: str
    body: str
    sender: str
    email_type: Optional[str] = "general"  # price, availability, complaint, general


class EmailReplyRequest(BaseModel):
    email: EmailContent
    auto_send: bool = False
    recipient: Optional[str] = None


class EmailReplyResponse(BaseModel):
    original_subject: str
    generated_reply: str
    status: str  # draft, sent
    generated_at: datetime


@router.post("/generate-reply", response_model=EmailReplyResponse)
async def generate_reply(request: EmailReplyRequest):
    """
    Генерация ответа на входящее письмо с помощью AI.
    
    Типы писем:
    - price: запрос цены
    - availability: наличие товара
    - complaint: жалоба
    - general: общий запрос
    """
    try:
        email_content = f"Тема: {request.email.subject}\n\nОт: {request.email.sender}\n\n{request.email.body}"
        
        reply = await generate_email_reply(
            email_content=email_content,
            email_type=request.email.email_type
        )
        
        status = "draft"
        
        # Если auto_send = True и есть получатель, отправляем
        # TODO: интеграция с Gmail API для отправки
        if request.auto_send and request.recipient:
            # await send_email(request.recipient, f"Re: {request.email.subject}", reply)
            status = "sent"
        
        return EmailReplyResponse(
            original_subject=request.email.subject,
            generated_reply=reply,
            status=status,
            generated_at=datetime.now()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка генерации ответа: {str(e)}")


@router.get("/templates")
async def get_email_templates():
    """Получить шаблоны ответов из базы знаний"""
    try:
        result = supabase.table("knowledge_base").select("*").eq("is_active", True).execute()
        return result.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/templates")
async def create_template(
    category: str,
    question: str,
    answer: str
):
    """Добавить шаблон ответа в базу знаний"""
    try:
        result = supabase.table("knowledge_base").insert({
            "category": category,
            "question": question,
            "answer": answer
        }).execute()
        return result.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class EmailClassifyRequest(BaseModel):
    subject: str
    body: str


@router.post("/classify")
async def classify_email(request: EmailClassifyRequest):
    """Классификация типа письма с помощью AI"""
    # Простая классификация по ключевым словам
    text = f"{request.subject} {request.body}".lower()
    
    if any(word in text for word in ['цена', 'стоимость', 'прайс', 'сколько стоит']):
        email_type = "price"
    elif any(word in text for word in ['наличие', 'есть ли', 'в наличии', 'остаток']):
        email_type = "availability"
    elif any(word in text for word in ['жалоба', 'претензия', 'недовольн', 'брак', 'проблема']):
        email_type = "complaint"
    else:
        email_type = "general"
    
    return {"email_type": email_type, "confidence": 0.85}
