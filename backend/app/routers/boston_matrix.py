from fastapi import APIRouter, Query, HTTPException
from datetime import date, datetime, timedelta
from typing import Optional, List
from pydantic import BaseModel
from app.database import supabase
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


class BostonProduct(BaseModel):
    """Product in Boston Matrix"""
    product_id: str
    name: str
    category: Optional[str] = None
    revenue: float
    revenue_growth: float  # % change vs previous period
    market_share: float  # % of total revenue
    quadrant: str  # "star", "cash_cow", "question_mark", "dog"


class BostonMatrixResponse(BaseModel):
    """Boston Matrix (BCG) analysis response"""
    products: List[BostonProduct]
    quadrant_counts: dict
    thresholds: dict
    total_revenue: float


def classify_quadrant(growth: float, share: float, growth_threshold: float, share_threshold: float) -> str:
    """
    Boston Matrix quadrant classification:
    - Star: High growth, High share (upper right)
    - Question Mark: High growth, Low share (upper left)
    - Cash Cow: Low growth, High share (lower right)
    - Dog: Low growth, Low share (lower left)
    """
    is_high_growth = growth >= growth_threshold
    is_high_share = share >= share_threshold
    
    if is_high_growth and is_high_share:
        return "star"
    elif is_high_growth and not is_high_share:
        return "question_mark"
    elif not is_high_growth and is_high_share:
        return "cash_cow"
    else:
        return "dog"


@router.get("/boston-matrix", response_model=BostonMatrixResponse)
async def get_boston_matrix(
    days: int = Query(default=90, ge=30, le=365, description="Текущий период в днях"),
    growth_threshold: float = Query(default=10.0, description="Порог роста (%)"),
    share_threshold: float = Query(default=5.0, description="Порог доли рынка (%)")
):
    """
    Boston Matrix (BCG) анализ продуктов.
    
    Классификация:
    - ⭐ Stars (Звезды): Высокий рост + Высокая доля → Инвестировать
    - ❓ Question Marks (Вопросы): Высокий рост + Низкая доля → Развивать или убрать
    - 🐄 Cash Cows (Дойные коровы): Низкий рост + Высокая доля → Поддерживать
    - 🐕 Dogs (Собаки): Низкий рост + Низкая доля → Избавляться
    """
    if supabase is None:
        return BostonMatrixResponse(
            products=[], 
            quadrant_counts={"star": 0, "question_mark": 0, "cash_cow": 0, "dog": 0},
            thresholds={"growth": growth_threshold, "share": share_threshold},
            total_revenue=0
        )
    
    try:
        # Current period
        current_end = date.today()
        current_start = current_end - timedelta(days=days)
        
        # Previous period (same length)
        prev_end = current_start - timedelta(days=1)
        prev_start = prev_end - timedelta(days=days)
        
        # Get current period sales
        current_result = supabase.table("sales").select(
            "product_id, total_amount"
        ).gte("sale_date", current_start.isoformat()).lte("sale_date", current_end.isoformat()).execute()
        
        # Get previous period sales
        prev_result = supabase.table("sales").select(
            "product_id, total_amount"
        ).gte("sale_date", prev_start.isoformat()).lte("sale_date", prev_end.isoformat()).execute()
        
        # Aggregate by product
        current_revenue = {}
        for sale in (current_result.data or []):
            pid = sale.get("product_id")
            if pid:
                current_revenue[pid] = current_revenue.get(pid, 0) + float(sale.get("total_amount", 0) or 0)
        
        prev_revenue = {}
        for sale in (prev_result.data or []):
            pid = sale.get("product_id")
            if pid:
                prev_revenue[pid] = prev_revenue.get(pid, 0) + float(sale.get("total_amount", 0) or 0)
        
        # Calculate total revenue
        total_revenue = sum(current_revenue.values())
        
        if total_revenue == 0:
            return BostonMatrixResponse(
                products=[],
                quadrant_counts={"star": 0, "question_mark": 0, "cash_cow": 0, "dog": 0},
                thresholds={"growth": growth_threshold, "share": share_threshold},
                total_revenue=0
            )
        
        # Get product names
        product_ids = list(current_revenue.keys())
        products_result = supabase.table("products").select("id, name, category").in_("id", product_ids).execute()
        product_lookup = {p["id"]: p for p in (products_result.data or [])}
        
        # Build products with classifications
        products = []
        for pid, revenue in current_revenue.items():
            prev_rev = prev_revenue.get(pid, 0)
            
            # Calculate growth
            if prev_rev > 0:
                growth = ((revenue - prev_rev) / prev_rev) * 100
            else:
                growth = 100.0 if revenue > 0 else 0.0
            
            # Calculate market share
            share = (revenue / total_revenue) * 100
            
            # Classify quadrant
            quadrant = classify_quadrant(growth, share, growth_threshold, share_threshold)
            
            product_info = product_lookup.get(pid, {})
            
            products.append(BostonProduct(
                product_id=pid,
                name=product_info.get("name", "Unknown"),
                category=product_info.get("category"),
                revenue=round(revenue, 2),
                revenue_growth=round(growth, 2),
                market_share=round(share, 2),
                quadrant=quadrant
            ))
        
        # Sort by revenue
        products.sort(key=lambda x: x.revenue, reverse=True)
        
        # Limit to top 50 for response size
        products = products[:50]
        
        # Count by quadrant
        quadrant_counts = {"star": 0, "question_mark": 0, "cash_cow": 0, "dog": 0}
        for p in products:
            quadrant_counts[p.quadrant] += 1
        
        return BostonMatrixResponse(
            products=products,
            quadrant_counts=quadrant_counts,
            thresholds={"growth": growth_threshold, "share": share_threshold},
            total_revenue=round(total_revenue, 2)
        )
        
    except Exception as e:
        logger.error(f"Boston Matrix error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
