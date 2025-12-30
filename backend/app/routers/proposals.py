from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from io import BytesIO
from app.database import supabase
from app.services.ai_service import generate_proposal_text
from app.services.document_service import generate_proposal_docx, generate_proposal_pdf

router = APIRouter()


class ProposalItem(BaseModel):
    product_id: Optional[str] = None
    product_name: str
    quantity: int
    price: float
    discount: float = 0


class ProposalRequest(BaseModel):
    customer_name: str
    customer_company: Optional[str] = None
    items: List[ProposalItem]
    conditions: Optional[str] = None
    valid_days: int = 30
    use_ai: bool = True


class ProposalResponse(BaseModel):
    id: str
    customer_name: str
    total_amount: float
    generated_text: Optional[str] = None
    created_at: datetime


@router.post("/generate", response_model=ProposalResponse)
async def generate_proposal(request: ProposalRequest):
    """
    Генерация коммерческого предложения.
    
    - use_ai=True: AI помогает составить текст предложения
    - use_ai=False: только расчёт суммы
    """
    try:
        # Расчёт суммы
        total = sum(
            item.quantity * item.price * (1 - item.discount / 100)
            for item in request.items
        )
        
        generated_text = None
        if request.use_ai:
            products = [
                {"name": item.product_name, "quantity": item.quantity, "price": item.price}
                for item in request.items
            ]
            generated_text = await generate_proposal_text(
                customer=request.customer_name,
                products=products,
                conditions=request.conditions or "Стандартные условия"
            )
        
        # Сохраняем в БД (опционально)
        proposal_id = f"KP-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        return ProposalResponse(
            id=proposal_id,
            customer_name=request.customer_name,
            total_amount=round(total, 2),
            generated_text=generated_text,
            created_at=datetime.now()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/export/docx")
async def export_docx(request: ProposalRequest):
    """Экспорт КП в формате Word (DOCX)"""
    try:
        total = sum(
            item.quantity * item.price * (1 - item.discount / 100)
            for item in request.items
        )
        
        items_data = [
            {
                "name": item.product_name,
                "quantity": item.quantity,
                "price": item.price,
                "amount": item.quantity * item.price * (1 - item.discount / 100)
            }
            for item in request.items
        ]
        
        docx_buffer = generate_proposal_docx(
            customer_name=request.customer_name,
            customer_company=request.customer_company,
            items=items_data,
            total=total,
            conditions=request.conditions,
            valid_days=request.valid_days
        )
        
        filename = f"KP_{request.customer_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.docx"
        
        return StreamingResponse(
            docx_buffer,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/export/pdf")
async def export_pdf(request: ProposalRequest):
    """Экспорт КП в формате PDF"""
    try:
        total = sum(
            item.quantity * item.price * (1 - item.discount / 100)
            for item in request.items
        )
        
        items_data = [
            {
                "name": item.product_name,
                "quantity": item.quantity,
                "price": item.price,
                "amount": item.quantity * item.price * (1 - item.discount / 100)
            }
            for item in request.items
        ]
        
        pdf_buffer = generate_proposal_pdf(
            customer_name=request.customer_name,
            customer_company=request.customer_company,
            items=items_data,
            total=total,
            conditions=request.conditions,
            valid_days=request.valid_days
        )
        
        filename = f"KP_{request.customer_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf"
        
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/products-suggest")
async def suggest_products(query: str = Query(..., min_length=2)):
    """Поиск товаров для добавления в КП"""
    try:
        result = supabase.table("products")\
            .select("id, name, price, category")\
            .ilike("name", f"%{query}%")\
            .limit(10)\
            .execute()
        return result.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
