from fastapi import APIRouter, Query, HTTPException
from datetime import date, datetime, timedelta
from typing import Optional, List
from app.database import supabase
from app.models.sales import DashboardMetrics, SalesTrend, TopCustomer, TopProduct
from app.services.cache_service import cache
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Cache keys
CACHE_DASHBOARD = "analytics:dashboard"
CACHE_TOP_PRODUCTS = "analytics:top_products"
CACHE_TOP_CUSTOMERS = "analytics:top_customers"
CACHE_SALES_TREND = "analytics:sales_trend"


@router.get("/dashboard", response_model=DashboardMetrics)
async def get_dashboard(
    start_date: Optional[date] = Query(None, description="Начало периода"),
    end_date: Optional[date] = Query(None, description="Конец периода"),
    customer_id: Optional[str] = Query(None, description="ID клиента"),
    agent_id: Optional[str] = Query(None, description="ID агента"),
    force_refresh: bool = Query(False, description="Принудительное обновление")
):
    """Основные метрики дашборда с кэшированием"""
    
    # Try cache first (only for requests without filters)
    cache_key = CACHE_DASHBOARD
    if not any([start_date, end_date, customer_id, agent_id]) and not force_refresh:
        cached = cache.get(cache_key)
        if cached:
            return DashboardMetrics(**cached)
    
    if supabase is None:
        return DashboardMetrics(
            total_revenue=0,
            total_sales=0,
            average_check=0,
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
        
        response_data = {
            "total_revenue": round(total_revenue, 2),
            "total_sales": total_sales,
            "average_check": round(avg_check, 2),
            "period_start": start_date,
            "period_end": end_date
        }
        
        # Cache only unfiltered requests
        if not any([start_date, end_date, customer_id, agent_id]):
            cache.set(cache_key, response_data)
        
        return DashboardMetrics(**response_data)
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/top-customers", response_model=List[TopCustomer])
async def get_top_customers(
    limit: int = Query(default=10, ge=1, le=50, description="Количество записей"),
    days: int = Query(default=365, ge=1, le=3650, description="За последние N дней"),
    force_refresh: bool = Query(False, description="Принудительное обновление")
):
    """Топ клиентов по выручке с кэшированием"""
    
    cache_key = f"{CACHE_TOP_CUSTOMERS}:{limit}:{days}"
    if not force_refresh:
        cached = cache.get(cache_key)
        if cached:
            return [TopCustomer(**c) for c in cached]
    
    if supabase is None:
        return []
    
    try:
        cutoff_date = (datetime.now() - timedelta(days=days)).date().isoformat()
        
        # Query sales with customer data
        result = supabase.table("sales").select(
            "customer_id, total_amount, sale_date"
        ).gte("sale_date", cutoff_date).execute()
        
        # Get customer names
        customers_result = supabase.table("customers").select("id, name").execute()
        customer_names = {c['id']: c['name'] for c in customers_result.data}
        
        client_totals = {}
        for sale in result.data:
            c_id = sale.get("customer_id", "")
            if not c_id:
                continue
            c_name = customer_names.get(c_id, "Неизвестный")
            
            if c_id not in client_totals:
                client_totals[c_id] = {"name": c_name, "total": 0, "orders": 0}
            client_totals[c_id]["total"] += float(sale.get("total_amount", 0) or 0)
            client_totals[c_id]["orders"] += 1
        
        sorted_clients = sorted(
            client_totals.items(),
            key=lambda x: x[1]["total"],
            reverse=True
        )[:limit]
        
        response_data = [
            {"customer_id": c_id, "name": data["name"], "total": round(data["total"], 2)}
            for c_id, data in sorted_clients
        ]
        
        cache.set(cache_key, response_data)
        return [TopCustomer(**c) for c in response_data]
    except Exception as e:
        logger.error(f"Top customers error: {e}")
        return []


@router.get("/top-products", response_model=List[TopProduct])
async def get_top_products(
    limit: int = Query(default=10, ge=1, le=50, description="Количество записей"),
    days: int = Query(default=365, ge=1, le=3650, description="За последние N дней"),
    force_refresh: bool = Query(False, description="Принудительное обновление")
):
    """Топ товаров по продажам с кэшированием"""
    
    cache_key = f"{CACHE_TOP_PRODUCTS}:{limit}:{days}"
    if not force_refresh:
        cached = cache.get(cache_key)
        if cached:
            return [TopProduct(**p) for p in cached]
    
    if supabase is None:
        return []
    
    try:
        cutoff_date = (datetime.now() - timedelta(days=days)).date().isoformat()
        
        # Get products directly (using total_revenue if available, otherwise return by name)
        products_result = supabase.table("products").select("id, name, category, total_revenue").execute()
        
        # Sort by total_revenue if available, otherwise alphabetically
        products_data = products_result.data or []
        
        # Filter products with revenue
        products_with_revenue = [
            p for p in products_data 
            if p.get("total_revenue") and float(p.get("total_revenue", 0)) > 0
        ]
        
        if products_with_revenue:
            sorted_products = sorted(
                products_with_revenue,
                key=lambda x: float(x.get("total_revenue", 0)),
                reverse=True
            )[:limit]
        else:
            # Fallback: just return first N products
            sorted_products = products_data[:limit]
        
        response_data = [
            {
                "product_id": p.get("id", ""),
                "name": p.get("name", "Неизвестный"),
                "total_quantity": 0,  # No quantity data available
                "total_amount": round(float(p.get("total_revenue", 0) or 0), 2)
            }
            for p in sorted_products
        ]
        
        cache.set(cache_key, response_data)
        return [TopProduct(**p) for p in response_data]
    except Exception as e:
        logger.error(f"Top products error: {e}")
        return []


@router.get("/sales-trend", response_model=List[SalesTrend])
async def get_sales_trend(
    period: str = Query(default="month", description="Период группировки: day, week, month"),
    days: int = Query(default=180, ge=7, le=730, description="За последние N дней"),
    force_refresh: bool = Query(False, description="Принудительное обновление")
):
    """Динамика продаж с кэшированием"""
    
    cache_key = f"{CACHE_SALES_TREND}:{period}:{days}"
    if not force_refresh:
        cached = cache.get(cache_key)
        if cached:
            return [SalesTrend(**t) for t in cached]
    
    if supabase is None:
        return []
    
    try:
        cutoff_date = (datetime.now() - timedelta(days=days)).date().isoformat()
        
        result = supabase.table("sales").select(
            "sale_date, total_amount"
        ).gte("sale_date", cutoff_date).order("sale_date").execute()
        
        period_totals = {}
        for sale in result.data:
            sale_date = sale.get("sale_date", "")
            if not sale_date:
                continue
            
            try:
                dt = datetime.fromisoformat(sale_date.replace("Z", ""))
            except:
                continue
            
            if period == "day":
                period_key = dt.strftime("%Y-%m-%d")
            elif period == "week":
                period_key = (dt - timedelta(days=dt.weekday())).strftime("%Y-%m-%d")
            else:
                period_key = dt.strftime("%Y-%m")
            
            if period_key not in period_totals:
                period_totals[period_key] = {"amount": 0, "count": 0}
            period_totals[period_key]["amount"] += float(sale.get("total_amount", 0))
            period_totals[period_key]["count"] += 1
        
        sorted_periods = sorted(period_totals.items(), key=lambda x: x[0])
        
        response_data = [
            {"period": p, "amount": round(data["amount"], 2), "count": data["count"]}
            for p, data in sorted_periods
        ]
        
        cache.set(cache_key, response_data)
        return [SalesTrend(**t) for t in response_data]
    except Exception as e:
        logger.error(f"Sales trend error: {e}")
        return []


@router.post("/refresh")
async def refresh_analytics():
    """Принудительное обновление всей аналитики — сброс кэша"""
    
    # Clear all analytics cache
    cleared = cache.invalidate_pattern("analytics:")
    
    return {
        "success": True,
        "message": "Кэш очищен. Данные будут загружены заново при следующем запросе.",
        "cleared_entries": cleared,
        "cache_stats": cache.get_stats()
    }


@router.get("/cache-stats")
async def get_cache_stats():
    """Статистика кэша"""
    return cache.get_stats()


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
