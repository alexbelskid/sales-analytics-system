from fastapi import APIRouter, Query, HTTPException
from datetime import date
from typing import Optional, List
from app.database import supabase
from app.models.sales import DashboardMetrics, SalesTrend, TopCustomer, TopProduct

router = APIRouter()


@router.get("/dashboard", response_model=DashboardMetrics)
async def get_dashboard(
    start_date: Optional[date] = Query(None, description="Начало периода"),
    end_date: Optional[date] = Query(None, description="Конец периода"),
    customer_id: Optional[str] = Query(None, description="ID клиента"),
    agent_id: Optional[str] = Query(None, description="ID агента")
):
    """
    Основные метрики дашборда:
    - Общая выручка
    - Количество продаж
    - Средний чек
    """
    # Return demo data if Supabase not configured
    if supabase is None:
        return DashboardMetrics(
            total_revenue=2450000,
            total_sales=156,
            average_check=15705,
            period_start=start_date,
            period_end=end_date
        )
    
    try:
        query = supabase.table("sales").select("*")
        
        if start_date:
            query = query.gte("sale_date", start_date.isoformat())
        if end_date:
            query = query.lte("sale_date", end_date.isoformat())
        if customer_id:
            query = query.eq("customer_id", customer_id)
        if agent_id:
            query = query.eq("agent_id", agent_id)
        
        result = query.execute()
        sales = result.data
        
        total_revenue = sum(float(s.get("total_amount", 0)) for s in sales)
        total_sales = len(sales)
        avg_check = total_revenue / total_sales if total_sales > 0 else 0
        
        return DashboardMetrics(
            total_revenue=round(total_revenue, 2),
            total_sales=total_sales,
            average_check=round(avg_check, 2),
            period_start=start_date,
            period_end=end_date
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/top-customers", response_model=List[TopCustomer])
async def get_top_customers(
    limit: int = Query(default=10, ge=1, le=50, description="Количество записей")
):
    """Топ клиентов по выручке"""
    if supabase is None:
        # Demo data
        return [
            TopCustomer(customer_id="1", name="ООО Альфа", total=450000),
            TopCustomer(customer_id="2", name="ИП Петров", total=380000),
            TopCustomer(customer_id="3", name="ЗАО Бета", total=320000),
        ]
    
    try:
        result = supabase.rpc("get_top_customers", {"limit_count": limit}).execute()
        return [TopCustomer(**row) for row in result.data]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/top-products", response_model=List[TopProduct])
async def get_top_products(
    limit: int = Query(default=10, ge=1, le=50, description="Количество записей")
):
    """Топ товаров по продажам"""
    if supabase is None:
        # Demo data
        return [
            TopProduct(product_id="1", name="Товар А", total_quantity=245, total_amount=367500),
            TopProduct(product_id="2", name="Товар Б", total_quantity=189, total_amount=283500),
            TopProduct(product_id="3", name="Товар В", total_quantity=156, total_amount=234000),
        ]
    
    try:
        result = supabase.rpc("get_top_products", {"limit_count": limit}).execute()
        return [TopProduct(**row) for row in result.data]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sales-trend", response_model=List[SalesTrend])
async def get_sales_trend(
    period: str = Query(default="month", description="Период группировки")
):
    """Динамика продаж (день/неделя/месяц)"""
    if supabase is None:
        # Demo data
        return [
            SalesTrend(period="2024-01", amount=1850000, count=45),
            SalesTrend(period="2024-02", amount=2100000, count=52),
            SalesTrend(period="2024-03", amount=1950000, count=48),
            SalesTrend(period="2024-04", amount=2300000, count=58),
            SalesTrend(period="2024-05", amount=2150000, count=54),
            SalesTrend(period="2024-06", amount=2450000, count=62),
        ]
    
    try:
        result = supabase.rpc("get_sales_trend", {"period_type": period}).execute()
        return [SalesTrend(**row) for row in result.data]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/customers")
async def get_customers():
    """Список всех клиентов"""
    if supabase is None:
        return []
    result = supabase.table("customers").select("*").execute()
    return result.data


@router.get("/products")
async def get_products():
    """Список всех товаров"""
    if supabase is None:
        return []
    result = supabase.table("products").select("*").execute()
    return result.data


@router.get("/agents")
async def get_agents():
    """Список всех агентов"""
    if supabase is None:
        return []
    result = supabase.table("agents").select("*").eq("is_active", True).execute()
    return result.data
