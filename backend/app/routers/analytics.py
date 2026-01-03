from fastapi import APIRouter, Query, HTTPException
from datetime import date, datetime, timedelta
from typing import Optional, List
from app.database import supabase
from app.models.sales import DashboardMetrics, SalesTrend, TopCustomer, TopProduct
import logging

logger = logging.getLogger(__name__)
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
        
        return DashboardMetrics(
            total_revenue=round(total_revenue, 2),
            total_sales=total_sales,
            average_check=round(avg_check, 2),
            period_start=start_date,
            period_end=end_date
        )
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/top-customers", response_model=List[TopCustomer])
async def get_top_customers(
    limit: int = Query(default=10, ge=1, le=50, description="Количество записей"),
    days: int = Query(default=365, ge=1, le=3650, description="За последние N дней")
):
    """Топ клиентов по выручке"""
    if supabase is None:
        return []
    
    try:
        cutoff_date = (datetime.now() - timedelta(days=days)).date().isoformat()
        
        # Fetch sales with customer names
        result = supabase.table("sales").select(
            "total_amount, customers(id, name)"
        ).gte("sale_date", cutoff_date).execute()
        
        # Aggregate by customer
        client_totals = {}
        for sale in result.data:
            customer = sale.get("customers", {})
            if not customer:
                continue
            c_id = customer.get("id", "")
            c_name = customer.get("name", "Неизвестный")
            
            if c_name not in client_totals:
                client_totals[c_name] = {"customer_id": c_id, "total": 0, "orders": 0}
            client_totals[c_name]["total"] += float(sale.get("total_amount", 0))
            client_totals[c_name]["orders"] += 1
        
        # Sort by total and limit
        sorted_clients = sorted(
            client_totals.items(),
            key=lambda x: x[1]["total"],
            reverse=True
        )[:limit]
        
        return [
            TopCustomer(
                customer_id=data["customer_id"],
                name=name,
                total=round(data["total"], 2)
            )
            for name, data in sorted_clients
        ]
    except Exception as e:
        logger.error(f"Top customers error: {e}")
        return []


@router.get("/top-products", response_model=List[TopProduct])
async def get_top_products(
    limit: int = Query(default=10, ge=1, le=50, description="Количество записей"),
    days: int = Query(default=365, ge=1, le=3650, description="За последние N дней")
):
    """Топ товаров по продажам"""
    if supabase is None:
        return []
    
    try:
        cutoff_date = (datetime.now() - timedelta(days=days)).date().isoformat()
        
        # Fetch sale items with product names and sale dates
        result = supabase.table("sale_items").select(
            "quantity, amount, products(id, name), sales!inner(sale_date)"
        ).gte("sales.sale_date", cutoff_date).execute()
        
        # Aggregate by product
        product_totals = {}
        for item in result.data:
            product = item.get("products", {})
            if not product:
                continue
            p_id = product.get("id", "")
            p_name = product.get("name", "Неизвестный")
            
            if p_name not in product_totals:
                product_totals[p_name] = {"product_id": p_id, "quantity": 0, "amount": 0}
            product_totals[p_name]["quantity"] += float(item.get("quantity", 0))
            product_totals[p_name]["amount"] += float(item.get("amount", 0))
        
        # Sort by amount (revenue) and limit
        sorted_products = sorted(
            product_totals.items(),
            key=lambda x: x[1]["amount"],
            reverse=True
        )[:limit]
        
        return [
            TopProduct(
                product_id=data["product_id"],
                name=name,
                total_quantity=int(data["quantity"]),
                total_amount=round(data["amount"], 2)
            )
            for name, data in sorted_products
        ]
    except Exception as e:
        logger.error(f"Top products error: {e}")
        return []


@router.get("/sales-trend", response_model=List[SalesTrend])
async def get_sales_trend(
    period: str = Query(default="month", description="Период группировки: day, week, month"),
    days: int = Query(default=180, ge=7, le=730, description="За последние N дней")
):
    """Динамика продаж (день/неделя/месяц)"""
    if supabase is None:
        return []
    
    try:
        cutoff_date = (datetime.now() - timedelta(days=days)).date().isoformat()
        
        result = supabase.table("sales").select(
            "sale_date, total_amount"
        ).gte("sale_date", cutoff_date).order("sale_date").execute()
        
        # Group by period
        period_totals = {}
        for sale in result.data:
            sale_date = sale.get("sale_date", "")
            if not sale_date:
                continue
            
            # Determine period key
            try:
                dt = datetime.fromisoformat(sale_date.replace("Z", ""))
            except:
                continue
            
            if period == "day":
                period_key = dt.strftime("%Y-%m-%d")
            elif period == "week":
                # Monday of the week
                period_key = (dt - timedelta(days=dt.weekday())).strftime("%Y-%m-%d")
            else:  # month
                period_key = dt.strftime("%Y-%m")
            
            if period_key not in period_totals:
                period_totals[period_key] = {"amount": 0, "count": 0}
            period_totals[period_key]["amount"] += float(sale.get("total_amount", 0))
            period_totals[period_key]["count"] += 1
        
        # Sort by period and convert to list
        sorted_periods = sorted(period_totals.items(), key=lambda x: x[0])
        
        return [
            SalesTrend(
                period=p,
                amount=round(data["amount"], 2),
                count=data["count"]
            )
            for p, data in sorted_periods
        ]
    except Exception as e:
        logger.error(f"Sales trend error: {e}")
        return []


@router.post("/refresh-aggregation")
async def refresh_aggregation():
    """Принудительное обновление агрегации (для совместимости)"""
    # В этой реализации агрегация происходит в реальном времени,
    # поэтому здесь просто проверяем что данные доступны
    if supabase is None:
        return {"success": False, "message": "Database not configured"}
    
    try:
        sales_count = len(supabase.table("sales").select("id").execute().data)
        products_count = len(supabase.table("products").select("id").execute().data)
        customers_count = len(supabase.table("customers").select("id").execute().data)
        
        return {
            "success": True,
            "message": "Данные обновлены",
            "stats": {
                "sales": sales_count,
                "products": products_count,
                "customers": customers_count
            }
        }
    except Exception as e:
        logger.error(f"Refresh error: {e}")
        return {"success": False, "message": str(e)}


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
