"""
Enhanced Data Context Service
Provides FULL access to ALL database tables for AI with smart caching

This service solves the problem of AI only seeing summarized/limited data.
It pre-loads and caches complete reference data (products, customers, agents)
and provides full access to transactional data when needed.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from app.database import supabase, supabase_admin
from app.config import settings
import asyncio
from functools import lru_cache

logger = logging.getLogger(__name__)

# Use admin client to bypass RLS
_db = supabase_admin or supabase


@dataclass
class DataCatalog:
    """Metadata about available data in the database"""
    total_sales: int
    total_customers: int
    total_products: int
    total_agents: int
    date_range_start: Optional[str]
    date_range_end: Optional[str]
    last_import_date: Optional[str]
    data_sources: List[str]
    categories: List[str]
    regions: List[str]


class EnhancedDataContextService:
    """
    Service that provides COMPLETE data access to AI.
    
    Features:
    - Pre-loads ALL reference data (products, customers, agents)
    - Provides full access to sales data without artificial limits
    - Smart caching to avoid repeated DB queries
    - Data catalog for AI to understand what's available
    """
    
    def __init__(self):
        self._cache: Dict[str, Any] = {}
        self._cache_timestamp: Dict[str, datetime] = {}
        self._cache_ttl_minutes = 10  # Cache reference data for 10 minutes
        
    async def _is_cache_valid(self, key: str) -> bool:
        """Check if cache entry is still valid"""
        if key not in self._cache or key not in self._cache_timestamp:
            return False
        
        age = (datetime.now() - self._cache_timestamp[key]).total_seconds() / 60
        return age < self._cache_ttl_minutes
    
    async def _set_cache(self, key: str, data: Any):
        """Store data in cache with timestamp"""
        self._cache[key] = data
        self._cache_timestamp[key] = datetime.now()
    
    async def get_all_products(self, force_refresh: bool = False) -> List[Dict[str, Any]]:
        """
        Get ALL products from database (no limits!)
        
        Returns:
            Complete list of all products with full details
        """
        cache_key = "all_products"
        
        if not force_refresh and await self._is_cache_valid(cache_key):
            logger.info(f"[CACHE HIT] Returning {len(self._cache[cache_key])} products from cache")
            return self._cache[cache_key]
        
        if not _db:
            return []
        
        try:
            # Fetch ALL products (no limit!)
            result = _db.table("products").select(
                "id, name, normalized_name, category, total_quantity, total_revenue, sales_count, created_at"
            ).order("total_revenue", desc=True).execute()
            
            products = result.data or []
            await self._set_cache(cache_key, products)
            
            logger.info(f"[DB FETCH] Loaded {len(products)} products from database")
            return products
            
        except Exception as e:
            logger.error(f"Error fetching all products: {e}")
            return []
    
    async def get_all_customers(self, force_refresh: bool = False) -> List[Dict[str, Any]]:
        """
        Get ALL customers from database (no limits!)
        
        Returns:
            Complete list of all customers with full details
        """
        cache_key = "all_customers"
        
        if not force_refresh and await self._is_cache_valid(cache_key):
            logger.info(f"[CACHE HIT] Returning {len(self._cache[cache_key])} customers from cache")
            return self._cache[cache_key]
        
        if not _db:
            return []
        
        try:
            # Fetch ALL customers (no limit!)
            result = _db.table("customers").select(
                "id, name, normalized_name, total_purchases, purchases_count, last_purchase_date, created_at"
            ).order("total_purchases", desc=True).execute()
            
            customers = result.data or []
            await self._set_cache(cache_key, customers)
            
            logger.info(f"[DB FETCH] Loaded {len(customers)} customers from database")
            return customers
            
        except Exception as e:
            logger.error(f"Error fetching all customers: {e}")
            return []
    
    async def get_all_agents(self, force_refresh: bool = False) -> List[Dict[str, Any]]:
        """
        Get ALL agents from database (no limits!)
        
        Returns:
            Complete list of all agents with full details
        """
        cache_key = "all_agents"
        
        if not force_refresh and await self._is_cache_valid(cache_key):
            logger.info(f"[CACHE HIT] Returning {len(self._cache[cache_key])} agents from cache")
            return self._cache[cache_key]
        
        if not _db:
            return []
        
        try:
            # Fetch ALL agents (no limit!)
            result = _db.table("agents").select(
                "id, name, email, phone, region, is_active, base_salary, commission_rate, created_at"
            ).execute()
            
            agents = result.data or []
            await self._set_cache(cache_key, agents)
            
            logger.info(f"[DB FETCH] Loaded {len(agents)} agents from database")
            return agents
            
        except Exception as e:
            logger.error(f"Error fetching all agents: {e}")
            return []
    
    async def get_data_catalog(self, force_refresh: bool = False) -> DataCatalog:
        """
        Get comprehensive metadata about available data
        
        This tells AI:
        - How much data is available
        - What time periods are covered
        - What categories/regions exist
        - When data was last updated
        
        Returns:
            DataCatalog object with complete metadata
        """
        cache_key = "data_catalog"
        
        if not force_refresh and await self._is_cache_valid(cache_key):
            logger.info("[CACHE HIT] Returning data catalog from cache")
            return self._cache[cache_key]
        
        if not _db:
            return DataCatalog(
                total_sales=0, total_customers=0, total_products=0, total_agents=0,
                date_range_start=None, date_range_end=None, last_import_date=None,
                data_sources=[], categories=[], regions=[]
            )
        
        try:
            # Count totals
            sales_count = _db.table("sales").select("id", count="exact").execute()
            customers_count = _db.table("customers").select("id", count="exact").execute()
            products_count = _db.table("products").select("id", count="exact").execute()
            agents_count = _db.table("agents").select("id", count="exact").execute()
            
            # Get date range
            date_range = _db.table("sales").select("sale_date").order(
                "sale_date", desc=False
            ).limit(1).execute()
            date_range_end = _db.table("sales").select("sale_date").order(
                "sale_date", desc=True
            ).limit(1).execute()
            
            # Get unique categories
            categories_result = _db.table("products").select("category").execute()
            categories = list(set(
                p.get("category") for p in (categories_result.data or []) 
                if p.get("category")
            ))
            
            # Get unique regions
            regions_result = _db.table("agents").select("region").execute()
            regions = list(set(
                a.get("region") for a in (regions_result.data or []) 
                if a.get("region")
            ))
            
            # Get last import info
            last_import = _db.table("import_history").select(
                "filename, completed_at"
            ).eq("status", "completed").order("completed_at", desc=True).limit(1).execute()
            
            data_sources = []
            last_import_date = None
            if last_import.data:
                data_sources = [imp.get("filename") for imp in last_import.data]
                last_import_date = last_import.data[0].get("completed_at")
            
            catalog = DataCatalog(
                total_sales=sales_count.count or 0,
                total_customers=customers_count.count or 0,
                total_products=products_count.count or 0,
                total_agents=agents_count.count or 0,
                date_range_start=date_range.data[0].get("sale_date") if date_range.data else None,
                date_range_end=date_range_end.data[0].get("sale_date") if date_range_end.data else None,
                last_import_date=last_import_date,
                data_sources=data_sources,
                categories=sorted(categories),
                regions=sorted(regions)
            )
            
            await self._set_cache(cache_key, catalog)
            logger.info(f"[DB FETCH] Created data catalog: {catalog.total_sales} sales, {catalog.total_products} products")
            
            return catalog
            
        except Exception as e:
            logger.error(f"Error creating data catalog: {e}")
            return DataCatalog(
                total_sales=0, total_customers=0, total_products=0, total_agents=0,
                date_range_start=None, date_range_end=None, last_import_date=None,
                data_sources=[], categories=[], regions=[]
            )
    
    async def get_sales_data(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        customer_id: Optional[str] = None,
        product_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get sales data with optional filters
        
        NO ARTIFICIAL LIMITS - returns ALL matching records unless limit specified
        
        Args:
            start_date: Filter by sale_date >= start_date
            end_date: Filter by sale_date <= end_date
            customer_id: Filter by specific customer
            product_id: Filter by specific product
            agent_id: Filter by specific agent
            limit: Optional limit (if None, returns ALL matching records)
        
        Returns:
            Complete list of matching sales records
        """
        if not _db:
            return []
        
        try:
            query = _db.table("sales").select(
                "id, sale_date, customer_id, product_id, store_id, quantity, price, total_amount, year, month"
            )
            
            if start_date:
                query = query.gte("sale_date", start_date)
            if end_date:
                query = query.lte("sale_date", end_date)
            if customer_id:
                query = query.eq("customer_id", customer_id)
            if product_id:
                query = query.eq("product_id", product_id)
            if agent_id:
                query = query.eq("agent_id", agent_id)
            
            query = query.order("sale_date", desc=True)
            
            if limit:
                query = query.limit(limit)
            
            result = query.execute()
            sales = result.data or []
            
            logger.info(f"[DB FETCH] Loaded {len(sales)} sales records (filters: start={start_date}, end={end_date})")
            return sales
            
        except Exception as e:
            logger.error(f"Error fetching sales data: {e}")
            return []
    
    async def get_complete_context_for_ai(
        self,
        include_all_products: bool = False,
        include_all_customers: bool = False,
        include_all_agents: bool = True,
        include_catalog: bool = True
    ) -> str:
        """
        Generate COMPLETE context string for AI with ALL available data
        
        Args:
            include_all_products: Include full product list (can be large!)
            include_all_customers: Include full customer list (can be large!)
            include_all_agents: Include full agent list
            include_catalog: Include data catalog metadata
        
        Returns:
            Formatted text context with COMPLETE data access information
        """
        lines = []
        lines.append("=" * 80)
        lines.append("ПОЛНЫЙ КОНТЕКСТ ДАННЫХ (COMPLETE DATA ACCESS)")
        lines.append("=" * 80)
        
        # Data Catalog
        if include_catalog:
            catalog = await self.get_data_catalog()
            lines.append("\n📊 КАТАЛОГ ДАННЫХ:")
            lines.append(f"• Всего продаж: {catalog.total_sales:,}")
            lines.append(f"• Всего клиентов: {catalog.total_customers:,}")
            lines.append(f"• Всего товаров: {catalog.total_products:,}")
            lines.append(f"• Всего агентов: {catalog.total_agents:,}")
            
            if catalog.date_range_start and catalog.date_range_end:
                lines.append(f"• Период данных: {catalog.date_range_start} по {catalog.date_range_end}")
            
            if catalog.last_import_date:
                lines.append(f"• Последнее обновление: {catalog.last_import_date}")
            
            if catalog.categories:
                lines.append(f"• Категории товаров ({len(catalog.categories)}): {', '.join(catalog.categories[:10])}")
                if len(catalog.categories) > 10:
                    lines.append(f"  ... и еще {len(catalog.categories) - 10}")
            
            if catalog.regions:
                lines.append(f"• Регионы ({len(catalog.regions)}): {', '.join(catalog.regions)}")
            
            if catalog.data_sources:
                lines.append(f"• Источники данных: {', '.join(catalog.data_sources[:3])}")
        
        # All Agents
        if include_all_agents:
            agents = await self.get_all_agents()
            lines.append(f"\n👥 ВСЕ АГЕНТЫ ({len(agents)}):")
            for i, agent in enumerate(agents[:20], 1):  # Show first 20 in context, rest available via SQL
                status = "✅" if agent.get("is_active") else "❌"
                lines.append(
                    f"  {i}. {status} {agent.get('name')} — "
                    f"Регион: {agent.get('region', 'N/A')} — "
                    f"Email: {agent.get('email', 'N/A')}"
                )
            if len(agents) > 20:
                lines.append(f"  ... и еще {len(agents) - 20} агентов (доступны через SQL запросы)")
        
        # All Products (summarized if too many)
        if include_all_products:
            products = await self.get_all_products()
            lines.append(f"\n📦 ВСЕ ТОВАРЫ ({len(products)}):")
            for i, product in enumerate(products[:30], 1):  # Show top 30 by revenue
                lines.append(
                    f"  {i}. {product.get('name')} — "
                    f"Категория: {product.get('category', 'N/A')} — "
                    f"Выручка: {product.get('total_revenue', 0):,.0f} BYN — "
                    f"Продаж: {product.get('sales_count', 0)}"
                )
            if len(products) > 30:
                lines.append(f"  ... и еще {len(products) - 30} товаров (доступны через SQL запросы)")
        
        # All Customers (summarized if too many)
        if include_all_customers:
            customers = await self.get_all_customers()
            lines.append(f"\n🏢 ВСЕ КЛИЕНТЫ ({len(customers)}):")
            for i, customer in enumerate(customers[:30], 1):  # Show top 30 by purchases
                lines.append(
                    f"  {i}. {customer.get('name')} — "
                    f"Покупок на: {customer.get('total_purchases', 0):,.0f} BYN — "
                    f"Заказов: {customer.get('purchases_count', 0)} — "
                    f"Последняя покупка: {customer.get('last_purchase_date', 'N/A')}"
                )
            if len(customers) > 30:
                lines.append(f"  ... и еще {len(customers) - 30} клиентов (доступны через SQL запросы)")
        
        lines.append("\n" + "=" * 80)
        lines.append("ВАЖНО: AI имеет доступ ко ВСЕМ данным через SQL запросы!")
        lines.append("Для детальных вопросов AI может запрашивать полные данные из БД.")
        lines.append("=" * 80)
        
        return "\n".join(lines)
    
    async def get_complete_data_for_ai_query(
        self,
        query: str,
        max_items_per_section: int = 100
    ) -> str:
        """
        STEP 4 FIX: Smart data loader for AI queries.
        Analyzes query and loads COMPLETE relevant data (not just summaries).
        
        This solves the problem of AI only seeing limited/summarized data
        by intelligently loading ALL relevant data based on the query.
        
        Args:
            query: User's question
            max_items_per_section: Maximum items to show in detail (rest summarized)
        
        Returns:
            Formatted data context with ALL relevant data for the query
        """
        lines = []
        query_lower = query.lower()
        
        lines.append("=" * 80)
        lines.append("🎯 ПОЛНЫЕ ДАННЫЕ ДЛЯ ВАШЕГО ЗАПРОСА")
        lines.append("=" * 80)
        
        # Analyze query for entities
        needs_products = any(word in query_lower for word in [
            'товар', 'продукт', 'product', 'категори', 'ассортимент'
        ])
        needs_agents = any(word in query_lower for word in [
            'агент', 'менеджер', 'продавец', 'сотрудник', 'регион'
        ])
        needs_customers = any(word in query_lower for word in [
            'клиент', 'покупател', 'заказчик', 'customer'
        ])
        
        # Check if user wants "all" data
        wants_all = any(word in query_lower for word in [
            'все', 'всех', 'полный список', 'complete', 'all'
        ])
        
        # Load COMPLETE product data if needed
        if needs_products:
            products = await self.get_all_products()
            lines.append(f"\n📦 ПОЛНЫЙ СПИСОК ТОВАРОВ ({len(products)} записей):")
            lines.append("=" * 80)
            
            # Check if query asks for specific category
            category_match = None
            for p in products:
                cat = p.get('category', '')
                if cat and cat.lower() in query_lower:
                    category_match = cat
                    break
            
            if category_match:
                # Filter by category
                filtered = [p for p in products if p.get('category') == category_match]
                lines.append(f"\n📂 Категория: {category_match} ({len(filtered)} товаров)")
                lines.append("-" * 80)
                
                for i, p in enumerate(filtered, 1):
                    lines.append(
                        f"{i:3d}. {p.get('name', 'Без названия'):50s} | "
                        f"Выручка: {p.get('total_revenue', 0):12,.0f} BYN | "
                        f"Продаж: {p.get('sales_count', 0):5d} | "
                        f"Кол-во: {p.get('total_quantity', 0):8,.0f}"
                    )
            elif wants_all or len(products) <= max_items_per_section:
                # Show ALL products
                lines.append("\n✅ ПОКАЗАНЫ ВСЕ ТОВАРЫ (полный доступ):")
                lines.append("-" * 80)
                
                # Group by category
                by_category = {}
                for p in products:
                    cat = p.get('category', 'Без категории')
                    if cat not in by_category:
                        by_category[cat] = []
                    by_category[cat].append(p)
                
                for cat in sorted(by_category.keys()):
                    items = by_category[cat]
                    lines.append(f"\n📂 {cat} ({len(items)} товаров):")
                    
                    for i, p in enumerate(sorted(items, key=lambda x: x.get('total_revenue', 0), reverse=True)[:20], 1):
                        lines.append(
                            f"  {i:2d}. {p.get('name', 'Без названия'):45s} | "
                            f"{p.get('total_revenue', 0):10,.0f} BYN"
                        )
                    
                    if len(items) > 20:
                        lines.append(f"     ... и еще {len(items) - 20} товаров")
            else:
                # Show top by revenue
                lines.append(f"\n🏆 ТОП-{max_items_per_section} товаров по выручке:")
                lines.append("-" * 80)
                
                sorted_products = sorted(products, key=lambda x: x.get('total_revenue', 0), reverse=True)
                for i, p in enumerate(sorted_products[:max_items_per_section], 1):
                    lines.append(
                        f"{i:3d}. {p.get('name', 'Без названия'):50s} | "
                        f"Категория: {p.get('category', 'N/A'):20s} | "
                        f"Выручка: {p.get('total_revenue', 0):12,.0f} BYN"
                    )
                
                if len(products) > max_items_per_section:
                    lines.append(f"\n💡 Всего {len(products)} товаров. Остальные доступны через SQL.")
        
        # Load COMPLETE agent data if needed
        if needs_agents:
            agents = await self.get_all_agents()
            lines.append(f"\n\n👥 ПОЛНЫЙ СПИСОК АГЕНТОВ ({len(agents)} записей):")
            lines.append("=" * 80)
            
            # Check for region filter
            region_match = None
            regions = ['минск', 'брест', 'витебск', 'гомель', 'гродно', 'могилев']
            for region in regions:
                if region in query_lower:
                    region_match = region.upper()
                    break
            
            if region_match:
                # Filter by region
                filtered = [a for a in agents if region_match in (a.get('region') or '').upper()]
                lines.append(f"\n🌍 Регион: {region_match} ({len(filtered)} агентов)")
                lines.append("-" * 80)
                
                for i, a in enumerate(filtered, 1):
                    status = "✅ Активен" if a.get('is_active') else "❌ Неактивен"
                    lines.append(
                        f"{i:3d}. {a.get('name', 'Без имени'):30s} | "
                        f"{status:12s} | "
                        f"Email: {a.get('email', 'N/A'):30s}"
                    )
            else:
                # Show all agents
                lines.append("\n✅ ПОКАЗАНЫ ВСЕ АГЕНТЫ:")
                lines.append("-" * 80)
                
                # Group by region
                by_region = {}
                for a in agents:
                    region = a.get('region', 'Без региона')
                    if region not in by_region:
                        by_region[region] = []
                    by_region[region].append(a)
                
                for region in sorted(by_region.keys()):
                    items = by_region[region]
                    active_count = sum(1 for a in items if a.get('is_active'))
                    lines.append(f"\n🌍 {region} ({len(items)} агентов, {active_count} активных):")
                    
                    for i, a in enumerate(items, 1):
                        status = "✅" if a.get('is_active') else "❌"
                        lines.append(
                            f"  {i:2d}. {status} {a.get('name', 'Без имени'):35s} | "
                            f"{a.get('email', 'N/A'):30s}"
                        )
        
        # Load COMPLETE customer data if needed
        if needs_customers:
            customers = await self.get_all_customers()
            lines.append(f"\n\n🏢 ПОЛНЫЙ СПИСОК КЛИЕНТОВ ({len(customers)} записей):")
            lines.append("=" * 80)
            
            if wants_all or len(customers) <= max_items_per_section:
                lines.append("\n✅ ПОКАЗАНЫ ВСЕ КЛИЕНТЫ:")
                lines.append("-" * 80)
                
                for i, c in enumerate(customers[:max_items_per_section], 1):
                    lines.append(
                        f"{i:3d}. {c.get('name', 'Без названия'):40s} | "
                        f"Покупок: {c.get('total_purchases', 0):12,.0f} BYN | "
                        f"Заказов: {c.get('purchases_count', 0):4d}"
                    )
                
                if len(customers) > max_items_per_section:
                    lines.append(f"\n💡 Показано {max_items_per_section} из {len(customers)}. Остальные доступны через SQL.")
            else:
                lines.append(f"\n🏆 ТОП-{max_items_per_section} клиентов по объему покупок:")
                lines.append("-" * 80)
                
                for i, c in enumerate(customers[:max_items_per_section], 1):
                    lines.append(
                        f"{i:3d}. {c.get('name', 'Без названия'):40s} | "
                        f"{c.get('total_purchases', 0):12,.0f} BYN"
                    )
        
        lines.append("\n" + "=" * 80)
        lines.append("✅ ВСЕ ДАННЫЕ ЗАГРУЖЕНЫ ИЗ БАЗЫ (полный доступ)")
        lines.append("💡 Для детальных запросов AI может использовать SQL")
        lines.append("=" * 80)
        
        return "\n".join(lines)
    
    async def clear_cache(self):
        """Clear all cached data (useful after imports)"""
        self._cache.clear()
        self._cache_timestamp.clear()
        logger.info("[CACHE] All caches cleared")


# Global singleton
enhanced_data_context = EnhancedDataContextService()
