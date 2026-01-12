from fastapi import APIRouter, Query, HTTPException
from datetime import date, datetime, timedelta
from typing import Optional, List, Dict, Any
from app.database import supabase
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


class LFLComparison(BaseModel):
    """Like-for-Like period comparison"""
    metric: str
    period1_value: float
    period2_value: float
    change_absolute: float
    change_percent: float
    period1_label: str
    period2_label: str


class FilterOptions(BaseModel):
    """Available filter options"""
    regions: List[str]
    categories: List[str]
    agents: List[Dict[str, str]]


@router.get("/filter-options", response_model=FilterOptions)
async def get_filter_options():
    """Получить доступные опции для фильтров"""
    if supabase is None:
        return FilterOptions(regions=[], categories=[], agents=[])
    
    try:
        # Get unique regions from customers
        customers = supabase.table("customers").select("region").execute()
        regions = list(set(c.get("region") for c in customers.data if c.get("region")))
        
        # Get unique categories from products
        products = supabase.table("products").select("category").execute()
        categories = list(set(p.get("category") for p in products.data if p.get("category")))
        
        # Get active agents
        agents_result = supabase.table("agents").select("id, name").eq("is_active", True).execute()
        agents = [{"id": a["id"], "name": a["name"]} for a in agents_result.data]
        
        return FilterOptions(
            regions=sorted(regions),
            categories=sorted(categories),
            agents=agents
        )
    except Exception as e:
        logger.error(f"Filter options error: {e}")
        return FilterOptions(regions=[], categories=[], agents=[])


@router.get("/lfl", response_model=List[LFLComparison])
async def get_lfl_comparison(
    period1_start: date = Query(..., description="Начало периода 1"),
    period1_end: date = Query(..., description="Конец периода 1"),
    period2_start: date = Query(..., description="Начало периода 2"),
    period2_end: date = Query(..., description="Конец периода 2"),
    customer_id: Optional[str] = Query(None, description="ID клиента"),
    product_id: Optional[str] = Query(None, description="ID продукта"),
    agent_id: Optional[str] = Query(None, description="ID агента")
):
    """
    Like-for-Like анализ - сравнение двух периодов.
    Например: этот месяц vs прошлый месяц, этот год vs прошлый год
    """
    if supabase is None:
        return []
    
    try:
        # Build filter conditions
        def build_query(start: date, end: date):
            query = supabase.table("sales").select("total_amount, quantity")
            query = query.gte("sale_date", start.isoformat())
            query = query.lte("sale_date", end.isoformat())
            
            if customer_id:
                query = query.eq("customer_id", customer_id)
            if product_id:
                query = query.eq("product_id", product_id)
            if agent_id:
                query = query.eq("agent_id", agent_id)
            
            return query.execute()
        
        # Get data for both periods
        period1_data = build_query(period1_start, period1_end)
        period2_data = build_query(period2_start, period2_end)
        
        # Calculate metrics for period 1
        p1_revenue = sum(float(r.get("total_amount", 0) or 0) for r in period1_data.data)
        p1_quantity = sum(float(r.get("quantity", 0) or 0) for r in period1_data.data)
        p1_orders = len(period1_data.data)
        
        # Calculate metrics for period 2
        p2_revenue = sum(float(r.get("total_amount", 0) or 0) for r in period2_data.data)
        p2_quantity = sum(float(r.get("quantity", 0) or 0) for r in period2_data.data)
        p2_orders = len(period2_data.data)
        
        # Build comparison results
        def calc_change(v1: float, v2: float) -> tuple:
            abs_change = v2 - v1
            pct_change = ((v2 - v1) / v1 * 100) if v1 > 0 else 0
            return abs_change, pct_change
        
        p1_label = f"{period1_start.strftime('%d.%m.%Y')} - {period1_end.strftime('%d.%m.%Y')}"
        p2_label = f"{period2_start.strftime('%d.%m.%Y')} - {period2_end.strftime('%d.%m.%Y')}"
        
        results = []
        
        # Revenue comparison
        rev_abs, rev_pct = calc_change(p1_revenue, p2_revenue)
        results.append(LFLComparison(
            metric="Выручка",
            period1_value=round(p1_revenue, 2),
            period2_value=round(p2_revenue, 2),
            change_absolute=round(rev_abs, 2),
            change_percent=round(rev_pct, 2),
            period1_label=p1_label,
            period2_label=p2_label
        ))
        
        # Quantity comparison
        qty_abs, qty_pct = calc_change(p1_quantity, p2_quantity)
        results.append(LFLComparison(
            metric="Количество",
            period1_value=round(p1_quantity, 2),
            period2_value=round(p2_quantity, 2),
            change_absolute=round(qty_abs, 2),
            change_percent=round(qty_pct, 2),
            period1_label=p1_label,
            period2_label=p2_label
        ))
        
        # Orders comparison
        ord_abs, ord_pct = calc_change(p1_orders, p2_orders)
        results.append(LFLComparison(
            metric="Заказы",
            period1_value=p1_orders,
            period2_value=p2_orders,
            change_absolute=ord_abs,
            change_percent=round(ord_pct, 2),
            period1_label=p1_label,
            period2_label=p2_label
        ))
        
        return results
        
    except Exception as e:
        logger.error(f"LFL comparison error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
