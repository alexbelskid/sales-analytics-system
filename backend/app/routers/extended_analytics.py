"""
Extended Analytics API Router
Provides analytics endpoints for imported Excel data
"""

from fastapi import APIRouter, Query
from typing import Optional
from app.services.extended_analytics_service import extended_analytics
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/ext-analytics", tags=["Extended Analytics"])


@router.get("/top-products")
async def get_top_products(
    limit: int = Query(default=10, ge=1, le=50, description="Количество товаров"),
    year: Optional[int] = Query(None, description="Год (например: 2024)"),
    month: Optional[int] = Query(None, ge=1, le=12, description="Месяц (1-12)"),
    store_id: Optional[str] = Query(None, description="ID магазина"),
    force_refresh: bool = Query(False, description="Обновить кэш")
):
    """
    Топ товаров по выручке
    
    Фильтры:
    - year: фильтр по году
    - month: фильтр по месяцу
    - store_id: фильтр по магазину
    """
    return extended_analytics.get_top_products(
        limit=limit,
        year=year,
        month=month,
        store_id=store_id,
        force_refresh=force_refresh
    )


@router.get("/top-customers")
async def get_top_customers(
    limit: int = Query(default=10, ge=1, le=50, description="Количество клиентов"),
    year: Optional[int] = Query(None, description="Год"),
    month: Optional[int] = Query(None, ge=1, le=12, description="Месяц"),
    force_refresh: bool = Query(False, description="Обновить кэш")
):
    """
    Топ клиентов по сумме покупок
    """
    return extended_analytics.get_top_customers(
        limit=limit,
        year=year,
        month=month,
        force_refresh=force_refresh
    )


@router.get("/sales-trend")
async def get_sales_trend(
    period: str = Query(default="month", description="Группировка: day, week, month"),
    year: Optional[int] = Query(None, description="Год"),
    force_refresh: bool = Query(False, description="Обновить кэш")
):
    """
    Динамика продаж по периодам
    
    Возвращает:
    - period: метка периода
    - amount: сумма продаж
    - count: количество сделок
    - average: средний чек
    """
    return extended_analytics.get_sales_trend(
        period=period,
        year=year,
        force_refresh=force_refresh
    )


@router.get("/summary")
async def get_summary(
    year: Optional[int] = Query(None, description="Год"),
    month: Optional[int] = Query(None, ge=1, le=12, description="Месяц"),
    force_refresh: bool = Query(False, description="Обновить кэш")
):
    """
    Общая статистика
    
    Возвращает:
    - total_revenue: общая выручка
    - total_sales: количество сделок
    - average_check: средний чек
    - unique_customers: уникальных клиентов
    - unique_products: уникальных товаров
    - top_product: топ товар
    - top_customer: топ клиент
    """
    return extended_analytics.get_summary(
        year=year,
        month=month,
        force_refresh=force_refresh
    )


@router.get("/sales-by-stores")
async def get_sales_by_stores(
    year: Optional[int] = Query(None, description="Год"),
    month: Optional[int] = Query(None, ge=1, le=12, description="Месяц"),
    force_refresh: bool = Query(False, description="Обновить кэш")
):
    """
    Продажи по магазинам/точкам
    """
    return extended_analytics.get_sales_by_stores(
        year=year,
        month=month,
        force_refresh=force_refresh
    )


@router.get("/available-years")
async def get_available_years():
    """
    Получить список доступных годов в данных
    """
    from app.database import supabase
    
    if supabase is None:
        return {'years': []}
    
    try:
        result = supabase.table('sales').select('year').execute()
        years = sorted(set(s['year'] for s in result.data if s.get('year')))
        return {'years': years}
    except Exception as e:
        logger.error(f"get_available_years error: {e}")
        return {'years': []}
